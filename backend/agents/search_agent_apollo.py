"""Search Agent for Apollo MCP Server using LangGraph"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import json
from datetime import datetime
import logging
import os

from mcp_servers.apollo_mcp_client import ApolloMCPClient

logger = logging.getLogger(__name__)

class SearchAgentState(TypedDict):
    """State for the search agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    search_params: Dict[str, Any]
    search_results: Dict[str, Any]
    property_details: Dict[str, Any]
    current_step: str
    agent_response: str

class SearchAgentApollo:
    """Agent for handling hotel search queries via Apollo MCP Server"""
    
    def __init__(self, llm, mcp_server_url: str):
        self.llm = llm
        self.mcp_client = ApolloMCPClient(mcp_server_url)
        self.workflow = self._create_workflow()
        
        # Get available tools from MCP server
        self.available_tools = self.mcp_client.get_available_tools()
        logger.info(f"Apollo MCP Search Agent initialized with {len(self.available_tools)} tools")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for search agent"""
        workflow = StateGraph(SearchAgentState)
        
        # Define workflow steps
        workflow.add_node("parse_query", self._parse_query)
        workflow.add_node("search_properties", self._search_properties)
        workflow.add_node("enrich_with_details", self._enrich_with_details)
        workflow.add_node("format_response", self._format_response)
        
        # Define workflow edges
        workflow.set_entry_point("parse_query")
        workflow.add_edge("parse_query", "search_properties")
        workflow.add_edge("search_properties", "enrich_with_details")
        workflow.add_edge("enrich_with_details", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_query(self, state: SearchAgentState) -> SearchAgentState:
        """Step 1: Parse user query to extract search parameters using LLM"""
        user_query = state['user_query']
        
        # Create tool schema description for LLM
        tools_description = json.dumps(self.available_tools, indent=2)
        
        # Use LLM to extract parameters based on MCP server schema
        system_prompt = f"""You are a hotel search parameter extractor for an Apollo MCP server.
        
Available MCP Tools:
{tools_description}

Analyze the user query and extract parameters for the 'searchrates' tool.
Extract: city, checkIn (YYYY-MM-DD), checkOut (YYYY-MM-DD), guests (number), brands (array of hotel brands if mentioned)

If the user asks about a specific property ID or wants details, also include: propertyId

Return ONLY a valid JSON object with the extracted parameters.
Example: {{"city": "Paris", "checkIn": "2025-02-01", "checkOut": "2025-02-05", "guests": 2, "brands": ["Marriott", "Sheraton"]}}

If dates are not provided, use reasonable defaults (7 days from today)."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            content = response.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            search_params = json.loads(content.strip())
        except Exception as e:
            logger.error(f"Error parsing search parameters: {e}")
            # Fallback to basic search
            search_params = {"city": "New York", "guests": 1}
        
        state['search_params'] = search_params
        state['current_step'] = 'parse_query'
        
        return state
    
    def _search_properties(self, state: SearchAgentState) -> SearchAgentState:
        """Step 2: Search for properties using Apollo MCP server"""
        params = state['search_params']
        
        logger.info(f"Searching properties with params: {params}")
        
        # Call MCP server's searchrates tool
        search_results = self.mcp_client.search_properties(
            city=params.get('city'),
            check_in=params.get('checkIn'),
            check_out=params.get('checkOut'),
            guests=params.get('guests', 1),
            brands=params.get('brands')
        )
        
        logger.info(f"Search results: {search_results}")
        
        state['search_results'] = search_results
        state['current_step'] = 'search_properties'
        
        return state
    
    def _enrich_with_details(self, state: SearchAgentState) -> SearchAgentState:
        """Step 3: Enrich results with property details and offers if available"""
        search_results = state['search_results']
        params = state['search_params']
        
        property_details = {}
        
        # If user asked about specific property or if we have property IDs in results
        if params.get('propertyId'):
            # Get specific property details
            details = self.mcp_client.get_property_details(params['propertyId'])
            offers = self.mcp_client.get_property_offers(params['propertyId'])
            
            property_details[params['propertyId']] = {
                "details": details,
                "offers": offers
            }
        
        # You can extend this to fetch details for top results from search
        # For now, keeping it simple
        
        state['property_details'] = property_details
        state['current_step'] = 'enrich_with_details'
        
        return state
    
    def _format_response(self, state: SearchAgentState) -> SearchAgentState:
        """Step 4: Format results into natural language response using LLM"""
        search_results = state['search_results']
        property_details = state['property_details']
        
        # Combine all data for LLM formatting
        context = {
            "search_results": search_results,
            "property_details": property_details
        }
        
        system_prompt = """You are a helpful hotel search assistant.
        Format the search results from the Apollo MCP server into a natural, conversational response.
        
        If the results contain properties:
        - List the hotel names with key details (location, rates, amenities)
        - Mention any special offers or promotions
        - Be informative but concise
        
        If there's an error or no results:
        - Explain the situation politely
        - Suggest alternatives or ask for different search criteria
        
        Make the response friendly and helpful."""
        
        context_text = json.dumps(context, indent=2)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Search results and property data:\n{context_text}")
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
            "property_details": {},
            "current_step": "",
            "agent_response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "agent": "search_agent_apollo",
            "response": final_state['agent_response'],
            "search_params": final_state['search_params'],
            "mcp_server": "apollo_graphql",
            "workflow_steps": ["parse_query", "search_properties", "enrich_with_details", "format_response"]
        }
    
    def get_mcp_server(self):
        """Return MCP client for server info"""
        return self.mcp_client