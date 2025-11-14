# Running Without Database

The AI Hotel Assistant can run **without MongoDB** for testing and development purposes. All core chat functionality works without a database.

## What Works Without Database

✅ **All Agent Functionality:**
- Search Agent (hotel searches)
- Booking Agent (hotel bookings)
- Customer Agent (customer data)

✅ **Chat Interface:**
- Send messages
- Receive AI responses
- View agent indicators
- All LangGraph workflows

✅ **MCP Server Integration:**
- All mock MCP servers work
- Remote MCP server connections work

## What Doesn't Work

❌ **Conversation History:**
- Conversations are not saved
- Cannot retrieve past conversations
- Each chat session is independent

❌ **Database Endpoints:**
- `POST /api/conversations` - Returns 503 error
- `GET /api/conversations/{id}` - Returns 503 error

## Quick Start Without Database

### Option 1: Docker Compose (Simplified)

```bash
# Use the simplified compose file without MongoDB
docker-compose -f docker-compose.simple.yml up --build
```

### Option 2: Comment Out MongoDB Config

Edit `backend/.env`:
```env
# Comment out or remove these lines:
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="hotel_assistant_db"
```

Then start normally:
```bash
docker-compose up --build
# OR
./start-local.sh
```

### Option 3: Manual Backend Start

```bash
cd backend

# Ensure MONGO_URL is not set
unset MONGO_URL

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## Verify Database is Disabled

Check the health endpoint:

```bash
curl http://localhost:8001/api/health
```

You should see:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "mongodb_available": false,
  ...
}
```

## Testing Chat Without Database

```bash
# Test chat endpoint
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find hotels in Paris for 2 guests"
  }'
```

Response will include the agent response without any database errors.

## Frontend Behavior

The frontend automatically adapts:
- Does not attempt to save conversation history
- All chat functionality remains available
- No error messages related to database

## When You Need a Database

You only need MongoDB if you want to:

1. **Save conversation history** - Store past chats for later retrieval
2. **User sessions** - Track user conversations over time
3. **Analytics** - Store data for analysis

For testing agents, MCP servers, and core chat functionality, **no database is needed**.

## Re-enabling Database Later

To add MongoDB back:

1. **Start MongoDB:**
   ```bash
   # Docker
   docker-compose up mongodb
   
   # OR install locally
   brew install mongodb-community@7.0  # Mac
   sudo apt-get install mongodb-org    # Ubuntu
   ```

2. **Update backend/.env:**
   ```env
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="hotel_assistant_db"
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

4. **Verify:**
   ```bash
   curl http://localhost:8001/api/health
   # Should show "mongodb_available": true
   ```

## Development Workflow

**Typical workflow without database:**

```bash
# 1. Clone repository
git clone <repo-url>
cd ai-hotel-assistant

# 2. Setup backend .env (no MongoDB needed)
cp backend/.env.example backend/.env
# Add only: OPENAI_API_KEY or ANTHROPIC_API_KEY

# 3. Start without MongoDB
docker-compose -f docker-compose.simple.yml up

# 4. Access at http://localhost:3000
# Chat works perfectly without database!
```

## Advantages of Running Without Database

✅ **Faster startup** - No MongoDB container to start
✅ **Less resources** - Saves memory and CPU
✅ **Simpler setup** - One less thing to configure
✅ **Easier testing** - Focus on agent functionality
✅ **No data cleanup** - No database to reset between tests

## Production Use

⚠️ **For production deployments, we recommend using MongoDB** to:
- Track user conversations
- Provide conversation history feature
- Enable analytics and monitoring
- Support multi-session user experience

---

For local testing and agent development, **MongoDB is completely optional**!
