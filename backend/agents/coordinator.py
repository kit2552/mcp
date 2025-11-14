"""Coordinator Agent to route queries to appropriate agents"""
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
import os

# Import LLM providers
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from agents.search_agent import SearchAgent
from agents.search_agent_apollo import SearchAgentApollo
from agents.booking_agent import BookingAgent
from agents.customer_agent import CustomerAgent

class AgentCoordinator:
    """Coordinates between multiple agents based on user intent"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        
        # Use Apollo MCP server for search if configured as remote
        search_server_type = os.getenv('MCP_SEARCH_SERVER_TYPE', 'mock')
        if search_server_type == 'remote':
            search_server_url = os.getenv('MCP_SEARCH_SERVER_URL')
            self.search_agent = SearchAgentApollo(self.llm, search_server_url)
        else:
            self.search_agent = SearchAgent(self.llm)
        
        self.booking_agent = BookingAgent(self.llm)
        self.customer_agent = CustomerAgent(self.llm)
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration"""
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            model = os.getenv('OPENAI_MODEL', 'gpt-4o')
            
            if not api_key or api_key == 'your-openai-api-key-here':
                raise ValueError("OPENAI_API_KEY not configured in .env file")
            
            return ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=float(os.getenv('AGENT_TEMPERATURE', '0.7'))
            )
        
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
            
            if not api_key or api_key == 'your-anthropic-api-key-here':
                raise ValueError("ANTHROPIC_API_KEY not configured in .env file")
            
            return ChatAnthropic(
                api_key=api_key,
                model=model,
                temperature=float(os.getenv('AGENT_TEMPERATURE', '0.7'))
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def route_query(self, user_message: str) -> Dict[str, Any]:
        """Route user query to appropriate agent"""
        
        # Determine intent using LLM
        intent = await self._determine_intent(user_message)
        
        if intent == 'search':
            result = await self.search_agent.process(user_message)
            return result
        
        elif intent == 'booking':
            result = await self.booking_agent.process(user_message)
            return result
        
        elif intent == 'customer':
            result = await self.customer_agent.process(user_message)
            return result
        
        else:
            # General response
            return {
                "agent": "coordinator",
                "response": "I can help you search for hotels, make bookings, or access your customer profile, trips, and rewards. What would you like to do?",
                "intent": "general"
            }
    
    async def _determine_intent(self, user_message: str) -> str:
        """Determine user intent from message"""
        system_prompt = """You are an intent classifier for a hotel assistant.
        Classify the user's message into one of these intents:
        - 'search': User wants to search for hotels, get hotel information, or browse options
        - 'booking': User wants to book a hotel, make a reservation, or confirm a booking
        - 'customer': User wants to view their profile, check trip history, see rewards/points, loyalty status, or vouchers
        - 'general': General queries or greetings
        
        Respond with ONLY one word: search, booking, customer, or general"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = self.llm.invoke(messages)
        intent = response.content.strip().lower()
        
        if 'search' in intent:
            return 'search'
        elif 'book' in intent:
            return 'booking'
        elif 'customer' in intent:
            return 'customer'
        else:
            return 'general'
    
    def get_mcp_server_info(self) -> Dict[str, Any]:
        """Get information about connected MCP servers"""
        # Get search agent tools based on type
        search_server_type = os.getenv('MCP_SEARCH_SERVER_TYPE', 'mock')
        if search_server_type == 'remote' and hasattr(self.search_agent, 'get_mcp_server'):
            search_tools = self.search_agent.get_mcp_server().get_available_tools()
        else:
            search_tools = self.search_agent.mcp_server.get_available_tools()
        
        return {
            "search_server": {
                "type": search_server_type,
                "url": os.getenv('MCP_SEARCH_SERVER_URL'),
                "tools": search_tools,
                "implementation": "apollo_graphql" if search_server_type == 'remote' else "mock"
            },
            "booking_server": {
                "type": os.getenv('MCP_BOOKING_SERVER_TYPE', 'mock'),
                "url": os.getenv('MCP_BOOKING_SERVER_URL'),
                "tools": self.booking_agent.mcp_server.get_available_tools()
            },
            "customer_server": {
                "type": os.getenv('MCP_CUSTOMER_SERVER_TYPE', 'mock'),
                "url": os.getenv('MCP_CUSTOMER_SERVER_URL'),
                "tools": self.customer_agent.mcp_server.get_available_tools()
            }
        }