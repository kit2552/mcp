"""Customer Agent for Customer Data Operations using LangGraph"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import json
from datetime import datetime

from mcp_servers.mock_customer_server import customer_server

class CustomerAgentState(TypedDict):
    """State for the customer agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    customer_params: Dict[str, Any]
    customer_data: Dict[str, Any]
    current_step: str
    agent_response: str

class CustomerAgent:
    """Agent for handling customer data queries"""
    
    def __init__(self, llm):
        self.llm = llm
        self.mcp_server = customer_server
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for customer agent"""
        workflow = StateGraph(CustomerAgentState)
        
        # Define workflow steps
        workflow.add_node("parse_customer_query", self._parse_customer_query)
        workflow.add_node("fetch_customer_data", self._fetch_customer_data)
        workflow.add_node("format_response", self._format_response)
        
        # Define workflow edges
        workflow.set_entry_point("parse_customer_query")
        workflow.add_edge("parse_customer_query", "fetch_customer_data")
        workflow.add_edge("fetch_customer_data", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_customer_query(self, state: CustomerAgentState) -> CustomerAgentState:
        """Step 1: Parse customer query to determine what data to fetch"""
        user_query = state['user_query']
        
        # Use LLM to extract parameters and determine query type
        system_prompt = """You are a customer data query analyzer.
        Analyze the user query and extract:
        1. customer_id or email (if mentioned)
        2. query_type: one of ['profile', 'trips', 'rewards', 'all']
        3. trip_status: if asking about trips, specify 'completed', 'upcoming', or null for all
        
        Return ONLY a JSON object.
        Example: {"customer_id": "customer_1", "email": null, "query_type": "trips", "trip_status": "upcoming"}"""
        
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
            
            customer_params = json.loads(content.strip())
        except:
            # Fallback: assume asking for all data
            customer_params = {"customer_id": "customer_1", "query_type": "all", "trip_status": None}
        
        state['customer_params'] = customer_params
        state['current_step'] = 'parse_customer_query'
        
        return state
    
    def _fetch_customer_data(self, state: CustomerAgentState) -> CustomerAgentState:
        """Step 2: Fetch customer data from MCP server"""
        params = state['customer_params']
        query_type = params.get('query_type', 'all')
        
        customer_data = {}
        
        # Fetch profile
        if query_type in ['profile', 'all']:
            profile_result = self.mcp_server.get_customer_profile(
                customer_id=params.get('customer_id'),
                email=params.get('email')
            )
            customer_data['profile'] = profile_result
            
            # If profile found, use customer_id for other queries
            if profile_result.get('success'):
                customer_id = profile_result['profile']['customer_id']
            else:
                # Profile not found, can't continue
                state['customer_data'] = customer_data
                state['current_step'] = 'fetch_customer_data'
                return state
        else:
            customer_id = params.get('customer_id')
        
        # Fetch trips
        if query_type in ['trips', 'all']:
            trips_result = self.mcp_server.get_customer_trips(
                customer_id=customer_id,
                status=params.get('trip_status')
            )
            customer_data['trips'] = trips_result
        
        # Fetch rewards
        if query_type in ['rewards', 'all']:
            rewards_result = self.mcp_server.get_customer_rewards(
                customer_id=customer_id
            )
            customer_data['rewards'] = rewards_result
        
        state['customer_data'] = customer_data
        state['current_step'] = 'fetch_customer_data'
        
        return state
    
    def _format_response(self, state: CustomerAgentState) -> CustomerAgentState:
        """Step 3: Format customer data into natural language response"""
        customer_data = state['customer_data']
        
        # Use LLM to format data
        system_prompt = """You are a helpful customer service assistant.
        Format the customer data into a friendly, conversational response.
        Include relevant details like profile info, trip history, rewards points, loyalty tier, and available vouchers.
        Be concise but informative."""
        
        data_text = json.dumps(customer_data, indent=2)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Customer data: {data_text}")
        ]
        
        response = self.llm.invoke(messages)
        state['agent_response'] = response.content
        state['current_step'] = 'format_response'
        
        return state
    
    async def process(self, user_query: str) -> Dict[str, Any]:
        """Process a customer data query"""
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "customer_params": {},
            "customer_data": {},
            "current_step": "",
            "agent_response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "agent": "customer_agent",
            "response": final_state['agent_response'],
            "customer_params": final_state['customer_params'],
            "data_retrieved": list(final_state['customer_data'].keys()),
            "workflow_steps": ["parse_customer_query", "fetch_customer_data", "format_response"]
        }