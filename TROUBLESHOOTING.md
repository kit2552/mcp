# Troubleshooting Guide

Common issues and solutions for the AI Hotel Assistant.

## 🔴 MongoDB Connection Errors

### Error: `ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused`

**Symptom:** Backend tries to connect to MongoDB even when you don't want to use it.

**Solutions:**

**Option 1: Use Simplified Docker Compose (No Database)**
```bash
# Use this instead of regular docker-compose
docker-compose -f docker-compose.simple.yml up --build
```

**Option 2: Ensure MongoDB Variables are NOT Set**

Check `backend/.env`:
```env
# These lines should be COMMENTED OUT or REMOVED:
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="hotel_assistant_db"
```

**Option 3: Override in Docker Compose**

The `docker-compose.simple.yml` now explicitly sets `MONGO_URL=` (empty) to disable MongoDB.

**Verify MongoDB is Disabled:**
```bash
# Check health endpoint
curl http://localhost:8001/api/health

# Should show: "mongodb_available": false
```

## 🔴 Invalid API Key Error

### Error: `Error code: 401 - {'error': {'message': 'Incorrect API key provided'...`

**Symptom:** Backend starts but chat requests fail with 401 error.

**Solutions:**

**1. Get a Valid API Key:**

For OpenAI:
- Go to: https://platform.openai.com/api-keys
- Create new API key
- Copy the full key (starts with `sk-proj-...`)

For Anthropic:
- Go to: https://console.anthropic.com/settings/keys
- Create new API key
- Copy the full key (starts with `sk-ant-...`)

**2. Update backend/.env:**

```env
# For OpenAI
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-proj-YOUR-ACTUAL-KEY-HERE"

# OR for Anthropic
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-YOUR-ACTUAL-KEY-HERE"
```

**3. Restart Backend:**
```bash
docker-compose restart backend
# OR
docker-compose -f docker-compose.simple.yml restart backend
```

**4. Verify Configuration:**
```bash
# Check health endpoint
curl http://localhost:8001/api/health

# Should show: "agent_initialized": true
```

**Common API Key Mistakes:**
- ❌ Key has expired
- ❌ Key was revoked in OpenAI/Anthropic dashboard
- ❌ Extra spaces before/after the key
- ❌ Wrong quotes or missing quotes
- ❌ Key truncated (incomplete)

## 🔴 Docker Build Errors

### Error: `The engine "node" is incompatible with this module`

**Solution:** Update `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine  # NOT node:18
```

### Error: `Cannot connect to the Docker daemon`

**Solutions:**
1. Start Docker Desktop
2. Check Docker is running: `docker ps`
3. Restart Docker service

## 🔴 Port Already in Use

### Error: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solutions:**

**Find what's using the port:**
```bash
# Mac/Linux
lsof -i :3000  # Frontend
lsof -i :8001  # Backend
lsof -i :27017 # MongoDB

# Kill the process
kill -9 <PID>
```

**Or change ports in docker-compose:**
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Use 3001 instead
  backend:
    ports:
      - "8002:8001"  # Use 8002 instead
```

## 🔴 Frontend Can't Connect to Backend

### Error: Network error or CORS error in browser console

**Solutions:**

**1. Verify Backend is Running:**
```bash
curl http://localhost:8001/api/health
```

**2. Check Backend URL in frontend/.env:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**3. Check CORS in backend/.env:**
```env
CORS_ORIGINS="http://localhost:3000"
```

**4. Clear Browser Cache:**
- Open DevTools (F12)
- Right-click refresh button → "Empty Cache and Hard Reload"

## 🔴 Environment Variables Not Loading

### Symptom: Changes to .env not reflected

**Solutions:**

**1. Restart Containers:**
```bash
docker-compose restart
# OR rebuild
docker-compose up --build
```

**2. Check .env File Location:**
```
✅ backend/.env (correct)
❌ .env (wrong location)
```

**3. No Quotes in Docker Environment:**

In `docker-compose.yml`:
```yaml
environment:
  - CORS_ORIGINS=http://localhost:3000  # No quotes
```

In `.env` file:
```env
CORS_ORIGINS="http://localhost:3000"  # Quotes OK
```

## 🔴 Container Keeps Restarting

**Check Logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common Causes:**
1. **Syntax error in code** - Check logs for Python/JavaScript errors
2. **Missing dependencies** - Rebuild: `docker-compose build --no-cache`
3. **Port conflict** - Change ports in docker-compose.yml
4. **Invalid configuration** - Check .env files

## 🔴 Hot Reload Not Working

### Changes to code not reflected

**Solutions:**

**For Backend (Python):**
```bash
# Restart backend
docker-compose restart backend

# Or check if uvicorn has --reload flag
docker-compose logs backend | grep reload
```

**For Frontend (React):**
```bash
# Restart frontend
docker-compose restart frontend

# Check if WDS_SOCKET_PORT is set
docker-compose logs frontend | grep WDS
```

**Volume Mounting Issues:**
```yaml
# Ensure volumes are mounted correctly
services:
  backend:
    volumes:
      - ./backend:/app  # Must be correct path
```

## 🔴 Database Connection Working But Chat Fails

**Check Agent Initialization:**
```bash
curl http://localhost:8001/api/health
```

Look for:
```json
{
  "agent_initialized": true  // Should be true
}
```

If `false`, check:
1. API key is valid
2. Backend logs for LLM errors
3. Network connectivity for remote MCP servers

## 🔴 MCP Server Connection Issues

### Error: Connection refused to MCP server

**For Mock Servers:**
- These are built-in, no external connection needed
- Set: `MCP_SEARCH_SERVER_TYPE="mock"`

**For Remote Apollo MCP Server:**
```env
MCP_SEARCH_SERVER_TYPE="remote"
MCP_SEARCH_SERVER_URL="https://your-mcp-server.com"
```

If connection fails:
- Check URL is correct
- Verify network access
- Check server is running
- Falls back to default schema automatically

## 📋 Validation Checklist

Before starting, run:
```bash
./validate-setup.sh
```

This checks:
- ✅ .env files exist
- ✅ API keys configured
- ✅ MongoDB config correct
- ✅ Ready to start

## 🔍 Debug Mode

### Enable Detailed Logging

**Backend:**
```python
# In server.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```bash
# Check browser console (F12)
# Look for network errors in Network tab
```

**Docker:**
```bash
# Follow logs in real-time
docker-compose logs -f backend
docker-compose logs -f frontend

# Get last 100 lines
docker-compose logs --tail=100 backend
```

## 🆘 Still Having Issues?

1. **Check all logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Clean rebuild:**
   ```bash
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Verify setup:**
   ```bash
   ./validate-setup.sh
   ```

4. **Test backend directly:**
   ```bash
   curl -X POST http://localhost:8001/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   ```

5. **Check documentation:**
   - [QUICKSTART.md](QUICKSTART.md)
   - [LOCAL_SETUP.md](LOCAL_SETUP.md)
   - [NO_DATABASE.md](NO_DATABASE.md)

---

**Pro Tip:** Most issues are solved by:
1. Valid API key in backend/.env
2. Using docker-compose.simple.yml for testing
3. Running validate-setup.sh before starting
