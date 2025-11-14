# Quick Setup Guide

## 🔧 Initial Configuration

### Step 1: Add Your OpenAI API Key

Edit `/app/backend/.env` and replace the placeholder with your actual OpenAI API key:

```env
OPENAI_API_KEY="sk-your-actual-openai-key-here"
```

**Where to get your OpenAI API key:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file

### Step 2: (Optional) Switch to Anthropic

If you prefer to use Anthropic Claude instead:

```env
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-your-actual-anthropic-key-here"
```

**Where to get your Anthropic API key:**
1. Go to https://console.anthropic.com/settings/keys
2. Sign in or create an account
3. Click "Create Key"
4. Copy the key and paste it in your `.env` file

### Step 3: Restart Backend

After updating the `.env` file:

```bash
sudo supervisorctl restart backend
```

### Step 4: Verify Setup

Check that the system is properly configured:

```bash
curl https://ai-travel-assistant-1.preview.emergentagent.com/api/health
```

You should see `"agent_initialized": true` if configured correctly.

## 🎯 Testing the System

### Test Hotel Search

```bash
curl -X POST "https://ai-travel-assistant-1.preview.emergentagent.com/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find hotels in Paris for 2 guests"
  }'
```

### Test via UI

1. Open: https://ai-travel-assistant-1.preview.emergentagent.com
2. Try these example queries:
   - "Find hotels in Paris for 2 guests"
   - "Show me luxury hotels in Tokyo with high ratings"
   - "Book hotel_1 from Jan 15 to Jan 20 for John Doe"

## 🔍 Troubleshooting

### Issue: "Agent not initialized" error

**Solution:** Your API key is not configured or invalid.
1. Check `/app/backend/.env` has correct API key
2. Verify key format starts with `sk-` (OpenAI) or `sk-ant-` (Anthropic)
3. Restart backend: `sudo supervisorctl restart backend`

### Issue: Backend not responding

**Solution:** Check backend logs:
```bash
tail -f /var/log/supervisor/backend.*.log
```

Look for error messages and verify:
- MongoDB is running
- All dependencies are installed
- No Python syntax errors

### Issue: Frontend shows connection error

**Solution:** 
1. Verify backend is running: `sudo supervisorctl status backend`
2. Test API directly: `curl https://ai-travel-assistant-1.preview.emergentagent.com/api/health`
3. Check CORS settings in backend `.env`

## 🚀 Next Steps

Once configured:

1. **Explore the UI**: Try different search and booking queries
2. **Check MCP Servers**: Visit `/api/mcp-servers` to see available tools
3. **View Workflow**: Check agent workflow steps in responses
4. **Customize Agents**: Modify workflow definitions in `agents/` directory
5. **Add Remote MCP Servers**: Update `.env` with remote server URLs

## 📚 Additional Resources

- Full documentation: `/app/README.md`
- Agent workflows: `/app/backend/agents/`
- MCP servers: `/app/backend/mcp_servers/`
- Frontend code: `/app/frontend/src/`

## 💡 Common Use Cases

### Switching LLM Providers

Edit `.env`:
```env
# Use OpenAI
LLM_PROVIDER="openai"

# OR use Anthropic
LLM_PROVIDER="anthropic"
```

Then restart: `sudo supervisorctl restart backend`

### Changing AI Model

```env
# OpenAI options
OPENAI_MODEL="gpt-4o"
OPENAI_MODEL="gpt-4-turbo"

# Anthropic options
ANTHROPIC_MODEL="claude-sonnet-4-20250514"
ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

### Connecting Remote MCP Servers

```env
MCP_SEARCH_SERVER_TYPE="remote"
MCP_SEARCH_SERVER_URL="https://your-mcp-server.com"
```

The system will automatically connect to your remote MCP server instead of using mock data.

---

Need help? Check the logs and README for detailed troubleshooting steps.
