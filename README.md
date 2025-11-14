# AI Hotel Assistant with Multi-Agent System

A sophisticated conversational AI chatbot powered by **LangGraph**, configurable LLMs (OpenAI/Anthropic), and Model Context Protocol (MCP) servers. This system uses multi-agent workflows to handle hotel search and booking operations.

## 🏗️ Architecture Overview

### Multi-Agent System
- **Coordinator Agent**: Routes user queries to appropriate specialized agents
- **Search Agent**: Handles hotel search operations via MCP search server
- **Booking Agent**: Manages hotel bookings via MCP booking server
- **Customer Agent**: Retrieves customer profile, trips, and rewards data via MCP customer server

### Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React with Tailwind CSS
- **Database**: MongoDB
- **AI Framework**: LangGraph for multi-agent workflows
- **LLM Support**: OpenAI (GPT-4o) or Anthropic (Claude Sonnet 4)
- **MCP Servers**: Mock implementations (configurable for remote servers)

## 🚀 Features

### ✨ Core Capabilities
- 🤖 **Multi-Agent Workflows**: Specialized agents for different tasks
- 🔄 **Configurable LLM**: Switch between OpenAI and Anthropic via environment variables
- 🛠️ **MCP Server Integration**: Modular tool system with mock implementations
- 📊 **Workflow Steps Configuration**: Define custom workflow steps for each agent
- 💬 **Conversational Interface**: Natural language hotel search and booking
- 📝 **Conversation History**: Persistent chat storage in MongoDB

### 🏨 Search Agent Workflow
1. **Parse Query**: Extract search parameters (location, dates, guests, filters)
2. **Search Hotels**: Query MCP search server with extracted parameters
3. **Filter Results**: Apply additional filters (rating, price, amenities, type)
4. **Format Response**: Generate natural language response with results

### 🎫 Booking Agent Workflow
1. **Parse Booking Request**: Extract booking details (hotel_id, dates, guest info)
2. **Check Availability**: Verify room availability via MCP booking server
3. **Create Booking**: Generate booking if available
4. **Confirm Booking**: Finalize and confirm the reservation
5. **Format Response**: Provide confirmation details or explain issues

### 👤 Customer Agent Workflow
1. **Parse Customer Query**: Determine query type (profile, trips, rewards, or all)
2. **Fetch Customer Data**: Query MCP customer server for requested information
3. **Format Response**: Present customer data in natural, conversational format

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py                          # FastAPI main server
│   ├── .env                                # Environment configuration
│   ├── requirements.txt                    # Python dependencies
│   ├── agents/
│   │   ├── coordinator.py                  # Coordinator agent
│   │   ├── search_agent.py                 # Search agent with LangGraph
│   │   ├── booking_agent.py                # Booking agent with LangGraph
│   │   └── customer_agent.py               # Customer agent with LangGraph
│   └── mcp_servers/
│       ├── mock_search_server.py           # Mock hotel search MCP server
│       ├── mock_booking_server.py          # Mock hotel booking MCP server
│       └── mock_customer_server.py         # Mock customer data MCP server
├── frontend/
│   ├── src/
│   │   ├── App.js                          # Main React component
│   │   ├── App.css                         # Styles
│   │   └── components/ui/                  # Shadcn UI components
│   └── package.json                        # Node dependencies
└── README.md
```

## ⚙️ Configuration

### Backend Environment Variables (.env)

```env
# MongoDB Configuration
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"

# LLM Configuration
LLM_PROVIDER="openai"                       # Options: openai, anthropic
OPENAI_API_KEY="your-openai-api-key-here"
ANTHROPIC_API_KEY="your-anthropic-api-key-here"
OPENAI_MODEL="gpt-4o"
ANTHROPIC_MODEL="claude-sonnet-4-20250514"

# MCP Server Configuration
MCP_SEARCH_SERVER_TYPE="mock"               # Options: mock, remote
MCP_SEARCH_SERVER_URL="http://localhost:8002"
MCP_BOOKING_SERVER_TYPE="mock"              # Options: mock, remote
MCP_BOOKING_SERVER_URL="http://localhost:8003"

# Agent Configuration
MAX_AGENT_ITERATIONS=10
AGENT_TEMPERATURE=0.7
```

### 🔑 Required Setup

1. **Configure LLM Provider**: Choose between OpenAI or Anthropic
   ```env
   LLM_PROVIDER="openai"
   OPENAI_API_KEY="sk-your-actual-key-here"
   ```

2. **Get API Keys**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys

3. **Restart Backend** after updating .env:
   ```bash
   sudo supervisorctl restart backend
   ```

## 🛠️ MCP Server System

### Current Implementation: Mock Servers

**Search Server Tools:**
- `search_hotels`: Search by location, dates, and guest count
- `get_hotel_details`: Get detailed information about specific hotels
- `filter_hotels`: Filter by rating, price, amenities, and type

**Booking Server Tools:**
- `check_availability`: Check room availability for dates
- `create_booking`: Create new hotel booking
- `confirm_booking`: Confirm and finalize booking
- `cancel_booking`: Cancel existing booking
- `get_booking_details`: Retrieve booking information

### Configuring Remote MCP Servers

To connect to remote MCP servers, update `.env`:

```env
# Switch to remote MCP servers
MCP_SEARCH_SERVER_TYPE="remote"
MCP_SEARCH_SERVER_URL="https://your-search-server.com"
MCP_BOOKING_SERVER_TYPE="remote"
MCP_BOOKING_SERVER_URL="https://your-booking-server.com"
```

The system will automatically connect to remote servers when configured. Mock servers provide full functionality for development and testing.

## 🔄 Agent Workflow Configuration

Each agent's workflow is defined in their respective files:

### Search Agent (`agents/search_agent.py`)
```python
# Workflow steps
workflow.add_node("parse_query", self._parse_query)
workflow.add_node("search_hotels", self._search_hotels)
workflow.add_node("filter_results", self._filter_results)
workflow.add_node("format_response", self._format_response)
```

### Booking Agent (`agents/booking_agent.py`)
```python
# Workflow steps
workflow.add_node("parse_booking_request", self._parse_booking_request)
workflow.add_node("check_availability", self._check_availability)
workflow.add_node("create_booking", self._create_booking)
workflow.add_node("confirm_booking", self._confirm_booking)
workflow.add_node("format_response", self._format_response)
```

You can customize these workflows by:
1. Adding new steps/nodes
2. Modifying edge connections
3. Adding conditional routing
4. Configuring tool parameters and headers per step

## 📡 API Endpoints

### Chat Endpoints
- `POST /api/chat`: Send message to chatbot
- `POST /api/conversations`: Create new conversation
- `GET /api/conversations/{id}`: Get conversation history

### System Endpoints
- `GET /api/health`: System health check
- `GET /api/mcp-servers`: Get MCP server information and available tools

### Example API Usage

```bash
# Send chat message
curl -X POST "${REACT_APP_BACKEND_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find hotels in Paris for 2 guests",
    "conversation_id": "conv_123"
  }'

# Get MCP server info
curl -X GET "${REACT_APP_BACKEND_URL}/api/mcp-servers"
```

## 💡 Example Queries

### Hotel Search
- "Find hotels in Paris for 2 guests"
- "Show me luxury hotels in Tokyo with ratings above 4.5"
- "Search for budget hotels in New York with WiFi and parking"
- "I need a hotel in London with a pool and gym"

### Hotel Booking
- "Book hotel_1 from January 15 to January 20 for John Doe"
- "I want to reserve hotel_5 for 2 rooms from Feb 1 to Feb 5"
- "Make a booking for hotel_10 with email john@example.com"

## 🔍 How It Works

1. **User Input**: User sends a natural language query
2. **Intent Classification**: Coordinator determines if it's search or booking
3. **Agent Selection**: Routes to Search Agent or Booking Agent
4. **Workflow Execution**: 
   - Agent executes multi-step LangGraph workflow
   - Each step can call MCP server tools
   - LLM processes results at each step
5. **Response Generation**: Agent formats natural language response
6. **Display**: UI shows response with agent and workflow metadata

## 🎨 Frontend Features

- **Real-time Chat Interface**: Smooth conversational experience
- **Agent Indicators**: Shows which agent handled the request
- **Status Monitoring**: Visual indication of system health
- **Example Prompts**: Quick-start suggestions
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Glass-morphism effects and smooth animations

## 🔐 Security Notes

- Store API keys securely in `.env` file
- Never commit `.env` to version control
- Use environment-specific configurations
- Implement rate limiting for production
- Add authentication for production deployments

## 🚀 Getting Started

1. **Configure API Keys** in `/app/backend/.env`
2. **Restart Backend**: `sudo supervisorctl restart backend`
3. **Access Application**: Open frontend URL in browser
4. **Start Chatting**: Try example prompts or ask your own questions

## 📊 Monitoring

Check system status:
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Check service status
sudo supervisorctl status
```

## 🛠️ Extending the System

### Add New Agent
1. Create agent file in `agents/` directory
2. Define LangGraph workflow with steps
3. Connect to MCP server tools
4. Register in coordinator

### Add New MCP Server
1. Create server implementation in `mcp_servers/`
2. Define available tools
3. Configure in `.env`
4. Connect agents to new server

### Add Custom Workflow Step
1. Define step function in agent class
2. Add node to workflow graph
3. Connect edges appropriately
4. Configure tool calls and headers

## 📝 Dependencies

**Backend:**
- fastapi
- langgraph
- langchain
- langchain-openai
- langchain-anthropic
- motor (MongoDB async driver)
- pydantic

**Frontend:**
- react
- axios
- lucide-react (icons)
- shadcn/ui components
- tailwindcss

## 🤝 Support

For issues or questions:
1. Check backend logs for errors
2. Verify API keys are configured correctly
3. Ensure MCP servers are accessible
4. Review LangGraph workflow definitions

---

Built with ❤️ using LangGraph, FastAPI, and React
