# Local Development Setup

This guide will help you run the AI Hotel Assistant application on your local machine.

## Prerequisites

### Option 1: Using Docker (Recommended)
- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Docker Compose v2.0+

### Option 2: Manual Setup
- Python 3.11+
- Node.js 18+
- MongoDB 7.0+
- yarn package manager

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-hotel-assistant
```

### 2. Configure Environment Variables

**Backend Configuration:**
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your API keys:
```env
OPENAI_API_KEY="sk-your-actual-openai-key"
# OR
ANTHROPIC_API_KEY="sk-ant-your-actual-anthropic-key"
```

**Frontend Configuration:**
```bash
cd ../frontend
cp .env.example .env
```

The default `.env` should work for local development.

### 3. Start the Application

From the root directory:

```bash
docker-compose up --build
```

This will start:
- MongoDB on `localhost:27017`
- Backend API on `http://localhost:8001`
- Frontend UI on `http://localhost:3000`

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

### 5. Stop the Application

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## Manual Setup (Without Docker)

### 1. Setup MongoDB

**Mac (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
Download and install from: https://www.mongodb.com/try/download/community

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend will be available at: `http://localhost:8001`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment
cp .env.example .env

# Start frontend
yarn start
```

Frontend will be available at: `http://localhost:3000`

## Configuration

### LLM Provider

Switch between OpenAI and Anthropic in `backend/.env`:

```env
# Use OpenAI
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-your-key"

# OR use Anthropic
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-your-key"
```

### MCP Servers

**Using Mock Servers (Default):**
```env
MCP_SEARCH_SERVER_TYPE="mock"
MCP_BOOKING_SERVER_TYPE="mock"
MCP_CUSTOMER_SERVER_TYPE="mock"
```

**Using Remote Apollo MCP Server:**
```env
MCP_SEARCH_SERVER_TYPE="remote"
MCP_SEARCH_SERVER_URL="https://uxl-mcp-mini-shop.uxl-platform.dev.cld.marriott.com/mcp"
```

## Testing the Setup

### 1. Check Backend Health

```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "llm_provider": "openai",
  "mcp_servers": {
    "search": "mock",
    "booking": "mock",
    "customer": "mock"
  }
}
```

### 2. Test Search Agent

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find hotels in Paris for 2 guests"}'
```

### 3. Test via UI

Open `http://localhost:3000` and try:
- "Find hotels in Tokyo"
- "Show me luxury hotels in New York"
- "Show me my profile for customer_1"

## Project Structure

```
ai-hotel-assistant/
├── backend/
│   ├── agents/              # LangGraph agents
│   │   ├── coordinator.py
│   │   ├── search_agent.py
│   │   ├── search_agent_apollo.py
│   │   ├── booking_agent.py
│   │   └── customer_agent.py
│   ├── mcp_servers/         # MCP server implementations
│   │   ├── mock_search_server.py
│   │   ├── mock_booking_server.py
│   │   ├── mock_customer_server.py
│   │   └── apollo_mcp_client.py
│   ├── server.py            # FastAPI application
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── components/ui/
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
├── LOCAL_SETUP.md
└── README.md
```

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Changes to Python files auto-reload
- Frontend: Changes to React files auto-reload

### View Logs

**Docker:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Manual setup:**
- Backend logs appear in the terminal where uvicorn is running
- Frontend logs appear in browser console and terminal

### Database Access

**Connect to MongoDB:**
```bash
# If using Docker
docker exec -it hotel-assistant-mongodb mongosh

# If running locally
mongosh
```

**View collections:**
```javascript
use hotel_assistant_db
show collections
db.conversations.find().pretty()
```

### Reset Database

**Docker:**
```bash
docker-compose down -v
docker-compose up
```

**Manual:**
```bash
mongosh
use hotel_assistant_db
db.dropDatabase()
```

## Troubleshooting

### Port Already in Use

If ports 3000, 8001, or 27017 are already in use:

1. Find the process:
```bash
# Mac/Linux
lsof -i :3000
lsof -i :8001
lsof -i :27017

# Windows
netstat -ano | findstr :3000
```

2. Kill the process or change ports in docker-compose.yml

### MongoDB Connection Failed

Ensure MongoDB is running:
```bash
# Docker
docker ps | grep mongodb

# Manual
# Mac
brew services list
# Linux
sudo systemctl status mongod
```

### API Key Not Working

1. Verify key in `backend/.env`
2. Ensure no extra quotes or spaces
3. Restart backend after changing .env
4. Check logs for specific error messages

### Frontend Can't Connect to Backend

1. Verify backend is running: `curl http://localhost:8001/api/health`
2. Check `frontend/.env` has correct `REACT_APP_BACKEND_URL`
3. Clear browser cache and reload
4. Check CORS settings in `backend/.env`

## Production Deployment

For production deployment:

1. **Update Environment Variables:**
   - Use production MongoDB URL
   - Set production CORS_ORIGINS
   - Use production frontend URL

2. **Build Optimized Images:**
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Use Environment-Specific Configs:**
   - Create `.env.production`
   - Update API endpoints
   - Enable SSL/TLS

4. **Security Checklist:**
   - Change default MongoDB credentials
   - Enable authentication on MongoDB
   - Use HTTPS for all endpoints
   - Set up API rate limiting
   - Secure API keys in vault service

## Support

For issues:
1. Check logs for error messages
2. Verify all environment variables are set
3. Ensure all services are running
4. Review README.md for additional documentation

---

Happy coding! 🚀