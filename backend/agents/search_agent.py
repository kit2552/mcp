"""Search Agent for Hotel Search Operations using LangGraph"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import json
from datetime import datetime

from mcp_servers.mock_search_server import search_server

class SearchAgentState(TypedDict):
    """State for the search agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    search_params: Dict[str, Any]
    search_results: Dict[str, Any]
    current_step: str
    agent_response: str

class SearchAgent:
    """Agent for handling hotel search queries"""
    
    def __init__(self, llm):
        self.llm = llm
        self.mcp_server = search_server
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for search agent"""
        workflow = StateGraph(SearchAgentState)
        
        # Define workflow steps
        workflow.add_node("parse_query", self._parse_query)
        workflow.add_node("search_hotels", self._search_hotels)
        workflow.add_node("filter_results", self._filter_results)
        workflow.add_node("format_response", self._format_response)
        
        # Define workflow edges
        workflow.set_entry_point("parse_query")
        workflow.add_edge("parse_query", "search_hotels")
        workflow.add_edge("search_hotels", "filter_results")
        workflow.add_edge("filter_results", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_query(self, state: SearchAgentState) -> SearchAgentState:
        """Step 1: Parse user query to extract search parameters"""
        user_query = state['user_query']
        
        # Use LLM to extract parameters
        system_prompt = """You are a hotel search parameter extractor. 
        Extract location, check_in date, check_out date, number of guests, and any filters (rating, price, amenities) from the user query.
        Return ONLY a JSON object with these fields. Use null for missing values.
        Example: {"location": "Paris", "check_in": "2025-01-15", "check_out": "2025-01-20", "guests": 2, "min_rating": 4.0, "max_price": 300}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Extract JSON from response
            content = response.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            search_params = json.loads(content.strip())
        except:
            # Fallback to basic parsing
            search_params = {"location": None, "check_in": None, "check_out": None, "guests": 1}
        
        state['search_params'] = search_params
        state['current_step'] = 'parse_query'
        
        return state
    
    def _search_hotels(self, state: SearchAgentState) -> SearchAgentState:
        """Step 2: Search hotels using MCP server"""
        params = state['search_params']
        
        # Call MCP search tool
        search_results = self.mcp_server.search_hotels(
            location=params.get('location'),
            check_in=params.get('check_in'),
            check_out=params.get('check_out'),
            guests=params.get('guests', 1)
        )
        
        state['search_results'] = search_results
        state['current_step'] = 'search_hotels'
        
        return state
    
    def _filter_results(self, state: SearchAgentState) -> SearchAgentState:
        """Step 3: Apply additional filters if specified"""
        params = state['search_params']
        search_results = state['search_results']
        
        # Check if additional filters are needed
        if params.get('min_rating') or params.get('max_price') or params.get('amenities') or params.get('hotel_type'):
            filtered_results = self.mcp_server.filter_hotels(
                min_rating=params.get('min_rating'),
                max_price=params.get('max_price'),
                amenities=params.get('amenities'),
                hotel_type=params.get('hotel_type')
            )
            state['search_results'] = filtered_results
        
        state['current_step'] = 'filter_results'
        
        return state
    
    def _format_response(self, state: SearchAgentState) -> SearchAgentState:
        """Step 4: Format results into natural language response"""
        search_results = state['search_results']
        
        # Use LLM to format results
        system_prompt = """You are a helpful hotel search assistant. 
        Format the search results into a natural, conversational response. 
        Include hotel names, locations, ratings, prices, and key amenities.
        Make it informative but concise."""
        
        results_text = json.dumps(search_results, indent=2)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Search results: {results_text}")
        ]
        
        response = self.llm.invoke(messages)
        state['agent_response'] = response.content
        state['current_step'] = 'format_response'
        
        return state
    
    async def process(self, user_query: str) -> Dict[str, Any]:
        """Process a search query"""
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "search_params": {},
            "search_results": {},
            "current_step": "",
            "agent_response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "agent": "search_agent",
            "response": final_state['agent_response'],
            "search_params": final_state['search_params'],
            "results_count": len(final_state['search_results'].get('results', [])),
            "workflow_steps": ["parse_query", "search_hotels", "filter_results", "format_response"]
        }