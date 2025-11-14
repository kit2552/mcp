from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import json

from agents.coordinator import AgentCoordinator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize agent coordinator
try:
    coordinator = AgentCoordinator()
    agent_initialized = True
except Exception as e:
    logging.error(f"Failed to initialize agent coordinator: {e}")
    coordinator = None
    agent_initialized = False

# Define Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent: Optional[str] = None
    metadata: Optional[dict] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: ChatMessage
    agent: str
    metadata: Optional[dict] = None

class ConversationHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Routes
@api_router.get("/")
async def root():
    return {"message": "AI Hotel Assistant API", "status": "running"}

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_initialized": agent_initialized,
        "llm_provider": os.getenv('LLM_PROVIDER', 'openai'),
        "mcp_servers": {
            "search": os.getenv('MCP_SEARCH_SERVER_TYPE', 'mock'),
            "booking": os.getenv('MCP_BOOKING_SERVER_TYPE', 'mock'),
            "customer": os.getenv('MCP_CUSTOMER_SERVER_TYPE', 'mock')
        }
    }

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot"""
    if not agent_initialized or not coordinator:
        raise HTTPException(status_code=500, detail="Agent system not initialized. Please configure API keys in .env file.")
    
    try:
        # Route query to appropriate agent
        result = await coordinator.route_query(request.message)
        
        # Create response message
        response_message = ChatMessage(
            role="assistant",
            content=result['response'],
            agent=result['agent'],
            metadata={
                "workflow_steps": result.get('workflow_steps', []),
                "intent": result.get('intent', '')
            }
        )
        
        # Store conversation in database if conversation_id provided
        if request.conversation_id:
            await _save_message(request.conversation_id, request.message, "user")
            await _save_message(request.conversation_id, result['response'], "assistant", result['agent'])
        
        return ChatResponse(
            message=response_message,
            agent=result['agent'],
            metadata=result
        )
    
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mcp-servers")
async def get_mcp_servers():
    """Get information about connected MCP servers and their tools"""
    if not coordinator:
        raise HTTPException(status_code=500, detail="Agent system not initialized")
    
    return coordinator.get_mcp_server_info()

@api_router.post("/conversations", response_model=ConversationHistory)
async def create_conversation():
    """Create a new conversation"""
    conversation = ConversationHistory()
    
    doc = conversation.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.conversations.insert_one(doc)
    
    return conversation

@api_router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Convert ISO strings back to datetime
    conversation['created_at'] = datetime.fromisoformat(conversation['created_at'])
    conversation['updated_at'] = datetime.fromisoformat(conversation['updated_at'])
    
    for msg in conversation.get('messages', []):
        if isinstance(msg['timestamp'], str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return ConversationHistory(**conversation)

async def _save_message(conversation_id: str, content: str, role: str, agent: str = None):
    """Helper to save message to conversation"""
    message = ChatMessage(role=role, content=content, agent=agent)
    message_dict = message.model_dump()
    message_dict['timestamp'] = message_dict['timestamp'].isoformat()
    
    await db.conversations.update_one(
        {"id": conversation_id},
        {
            "$push": {"messages": message_dict},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        },
        upsert=True
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()