"""Booking Agent for Hotel Booking Operations using LangGraph"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import json
from datetime import datetime

from mcp_servers.mock_booking_server import booking_server

class BookingAgentState(TypedDict):
    """State for the booking agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    booking_params: Dict[str, Any]
    availability_check: Dict[str, Any]
    booking_result: Dict[str, Any]
    current_step: str
    agent_response: str

class BookingAgent:
    """Agent for handling hotel booking operations"""
    
    def __init__(self, llm):
        self.llm = llm
        self.mcp_server = booking_server
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for booking agent"""
        workflow = StateGraph(BookingAgentState)
        
        # Define workflow steps
        workflow.add_node("parse_booking_request", self._parse_booking_request)
        workflow.add_node("check_availability", self._check_availability)
        workflow.add_node("create_booking", self._create_booking)
        workflow.add_node("confirm_booking", self._confirm_booking)
        workflow.add_node("format_response", self._format_response)
        
        # Define workflow edges
        workflow.set_entry_point("parse_booking_request")
        workflow.add_edge("parse_booking_request", "check_availability")
        workflow.add_conditional_edges(
            "check_availability",
            self._should_proceed_to_booking,
            {
                "create_booking": "create_booking",
                "format_response": "format_response"
            }
        )
        workflow.add_edge("create_booking", "confirm_booking")
        workflow.add_edge("confirm_booking", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_booking_request(self, state: BookingAgentState) -> BookingAgentState:
        """Step 1: Parse booking request from user query"""
        user_query = state['user_query']
        
        # Use LLM to extract booking parameters
        system_prompt = """You are a hotel booking parameter extractor.
        Extract hotel_id, check_in date, check_out date, guest_name, guest_email, number of rooms from the user query.
        Return ONLY a JSON object with these fields. Use null for missing values.
        Example: {"hotel_id": "hotel_1", "check_in": "2025-01-15", "check_out": "2025-01-20", "guest_name": "John Doe", "guest_email": "john@example.com", "rooms": 1}"""
        
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
            
            booking_params = json.loads(content.strip())
        except:
            booking_params = {}
        
        state['booking_params'] = booking_params
        state['current_step'] = 'parse_booking_request'
        
        return state
    
    def _check_availability(self, state: BookingAgentState) -> BookingAgentState:
        """Step 2: Check room availability"""
        params = state['booking_params']
        
        if not params.get('hotel_id'):
            state['availability_check'] = {"success": False, "error": "Missing hotel_id"}
            return state
        
        # Call MCP availability check tool
        availability = self.mcp_server.check_availability(
            hotel_id=params['hotel_id'],
            check_in=params.get('check_in', ''),
            check_out=params.get('check_out', ''),
            rooms=params.get('rooms', 1)
        )
        
        state['availability_check'] = availability
        state['current_step'] = 'check_availability'
        
        return state
    
    def _should_proceed_to_booking(self, state: BookingAgentState) -> str:
        """Decide whether to proceed with booking based on availability"""
        availability = state['availability_check']
        
        if availability.get('success') and availability.get('available'):
            return "create_booking"
        else:
            return "format_response"
    
    def _create_booking(self, state: BookingAgentState) -> BookingAgentState:
        """Step 3: Create the booking"""
        params = state['booking_params']
        
        # Call MCP create booking tool
        booking_result = self.mcp_server.create_booking(
            hotel_id=params['hotel_id'],
            check_in=params.get('check_in', ''),
            check_out=params.get('check_out', ''),
            guest_name=params.get('guest_name', 'Guest'),
            guest_email=params.get('guest_email', 'guest@example.com'),
            rooms=params.get('rooms', 1)
        )
        
        state['booking_result'] = booking_result
        state['current_step'] = 'create_booking'
        
        return state
    
    def _confirm_booking(self, state: BookingAgentState) -> BookingAgentState:
        """Step 4: Confirm the booking"""
        booking_result = state['booking_result']
        
        if booking_result.get('success'):
            booking_id = booking_result['booking']['booking_id']
            
            # Call MCP confirm booking tool
            confirmation = self.mcp_server.confirm_booking(booking_id)
            state['booking_result'] = confirmation
        
        state['current_step'] = 'confirm_booking'
        
        return state
    
    def _format_response(self, state: BookingAgentState) -> BookingAgentState:
        """Step 5: Format booking result into natural language"""
        availability = state['availability_check']
        booking_result = state.get('booking_result', {})
        
        # Use LLM to format response
        system_prompt = """You are a helpful hotel booking assistant.
        Format the booking information into a natural, conversational response.
        If booking was successful, include confirmation details.
        If not available or failed, explain why and offer alternatives."""
        
        context = {
            "availability": availability,
            "booking": booking_result
        }
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Booking context: {json.dumps(context, indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        state['agent_response'] = response.content
        state['current_step'] = 'format_response'
        
        return state
    
    async def process(self, user_query: str) -> Dict[str, Any]:
        """Process a booking request"""
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "booking_params": {},
            "availability_check": {},
            "booking_result": {},
            "current_step": "",
            "agent_response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "agent": "booking_agent",
            "response": final_state['agent_response'],
            "booking_params": final_state['booking_params'],
            "booking_status": final_state.get('booking_result', {}).get('booking', {}).get('status', 'unknown'),
            "workflow_steps": ["parse_booking_request", "check_availability", "create_booking", "confirm_booking", "format_response"]
        }