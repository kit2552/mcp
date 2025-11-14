# Quick Start Guide

Get the AI Hotel Assistant running on your local machine in 5 minutes!

## Prerequisites

✅ Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
✅ Git installed
✅ OpenAI or Anthropic API key

> **Note:** If running manually without Docker, you need Node.js 20+ (not 18)

## Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd ai-hotel-assistant
```

## Step 2: Configure API Keys

Create backend environment file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API key:

**For OpenAI:**
```env
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-your-actual-openai-key-here"
```

**For Anthropic:**
```env
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-your-actual-anthropic-key-here"
```

## Step 3: Start the Application

**Option A: With Database (Full Features)**
```bash
# Mac/Linux
./start-local.sh

# Windows
start-local.bat

# Or directly
docker-compose up --build
```

**Option B: Without Database (Faster, Testing Only)**
```bash
# Simpler setup - no MongoDB needed!
docker-compose -f docker-compose.simple.yml up --build
```

> 💡 **Tip:** For testing agents and chat functionality, you don't need MongoDB. See [NO_DATABASE.md](NO_DATABASE.md) for details.

## Step 4: Access the Application

Wait for all services to start (30-60 seconds), then open:

🌐 **Frontend:** http://localhost:3000

🔧 **Backend API:** http://localhost:8001

📊 **API Docs:** http://localhost:8001/docs

## Step 5: Test It Out

Try these example queries in the chat:

1. **Search Hotels:** "Find hotels in Paris for 2 guests"
2. **Book Hotel:** "Book hotel_1 from March 1 to March 5 for John Doe"
3. **Customer Info:** "Show me my profile and rewards for customer_1"

## Verify Everything Works

### Check Backend Health

```bash
curl http://localhost:8001/api/health
```

You should see:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "llm_provider": "openai",
  "mcp_servers": {...}
}
```

### Check MCP Servers

```bash
curl http://localhost:8001/api/mcp-servers
```

## Stopping the Application

Press `Ctrl+C` in the terminal, then:

```bash
docker-compose down
```

## Troubleshooting

### Node Version Error

**Error:** `The engine "node" is incompatible with this module. Expected version ">=20.0.0"`

**Solution:** The frontend requires Node.js 20+. Update your Dockerfile or local Node installation:

```bash
# Check Node version
node --version

# If using Docker, the Dockerfile should have:
FROM node:20-alpine  # NOT node:18-alpine

# If running manually, install Node 20+:
# Mac: brew install node@20
# Ubuntu: Use nvm or NodeSource
```

### Port Already in Use

If you get port conflicts:

```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8001  # Backend
lsof -i :27017 # MongoDB

# Kill the process or change ports in docker-compose.yml
```

### API Key Not Working

1. Make sure there are no extra spaces or quotes in your .env file
2. Restart the containers after changing .env:
   ```bash
   docker-compose restart backend
   ```

### Can't Connect to Backend

1. Check if backend is running:
   ```bash
   docker-compose ps
   ```

2. View backend logs:
   ```bash
   docker-compose logs backend
   ```

### MongoDB Connection Issues

```bash
# Restart MongoDB
docker-compose restart mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

## What's Next?

📚 **Full Documentation:** See [LOCAL_SETUP.md](LOCAL_SETUP.md)

🚀 **Deployment Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

🔧 **Customization:**
- Switch between OpenAI and Anthropic
- Configure remote MCP servers
- Add custom agents
- Modify UI styling

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │  React + Tailwind
│  localhost:3000 │  
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + LangGraph
│  localhost:8001 │  
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌────────┐ ┌─────┐ ┌─────────┐ ┌────────┐
│MongoDB │ │ MCP │ │   MCP   │ │  MCP   │
│  DB    │ │Search│ │ Booking │ │Customer│
└────────┘ └─────┘ └─────────┘ └────────┘
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify .env configuration
3. See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed troubleshooting

Happy coding! 🎉