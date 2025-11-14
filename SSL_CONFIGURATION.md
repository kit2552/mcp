# SSL/TLS Configuration Guide

This guide explains how SSL certificate verification is handled for remote MCP servers.

## Overview

When connecting to remote MCP servers (like the Apollo GraphQL MCP server), SSL/TLS certificate verification may need to be disabled for development and internal servers.

## Python Backend (Apollo MCP Client)

The Apollo MCP client in Python uses **httpx** library and already has SSL verification disabled:

```python
# In /app/backend/mcp_servers/apollo_mcp_client.py
self.client = httpx.Client(timeout=30.0, verify=False)
```

### What This Does

- **`verify=False`** - Disables SSL certificate verification
- Allows connections to servers with self-signed certificates
- Suppresses SSL warnings automatically

### When You Need This

✅ **Development/Internal Servers:**
- Internal corporate servers
- Development environments
- Self-signed certificates
- Private certificate authorities

❌ **Production (Not Recommended):**
- Public production servers should use valid certificates
- Consider using proper CA certificates instead

## Node.js Environment Variable

If you were using Node.js for MCP client connections, you would set:

```bash
# For Node.js applications only
export NODE_TLS_REJECT_UNAUTHORIZED="0"
```

**Note:** Our Apollo MCP client is written in **Python**, not Node.js, so this variable is **not needed** for this project.

## Configuration Status

### ✅ Already Configured

**Backend (Python):**
- SSL verification disabled in `apollo_mcp_client.py`
- Warnings suppressed automatically
- Works with self-signed certificates

**No Additional Configuration Needed!**

## Docker Environment

If you need to set environment variables in Docker:

### docker-compose.yml
```yaml
services:
  backend:
    environment:
      # Python doesn't need NODE_TLS_REJECT_UNAUTHORIZED
      # SSL is already disabled in code
      - PYTHONHTTPSVERIFY=0  # Alternative Python method (optional)
```

### Dockerfile
```dockerfile
# Not needed - already handled in code
# ENV NODE_TLS_REJECT_UNAUTHORIZED=0
```

## Testing SSL Configuration

### Test 1: Connection to Apollo MCP Server

```bash
# Backend should connect without SSL errors
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find hotels in Paris"}'

# Check logs - should NOT see SSL errors
docker-compose logs backend | grep -i ssl
```

### Test 2: Direct Python Test

```python
import httpx
import warnings
warnings.filterwarnings('ignore')

# This should work with self-signed certs
client = httpx.Client(verify=False)
response = client.get("https://uxl-mcp-mini-shop.uxl-platform.dev.cld.marriott.com/mcp/tools")
print(response.status_code)
```

## Security Considerations

### Development
✅ **Disabling SSL verification is acceptable:**
- Testing against internal servers
- Development environments
- Self-signed certificates for testing

### Production
⚠️ **Consider proper SSL setup:**

**Option 1: Use Valid Certificates**
```python
# Enable verification with proper certs
client = httpx.Client(verify=True)
```

**Option 2: Provide CA Certificate**
```python
# Use custom CA bundle
client = httpx.Client(verify="/path/to/ca-bundle.crt")
```

**Option 3: System CA Store**
```python
# Use system certificates
client = httpx.Client(verify=True)
```

## Troubleshooting

### SSL Certificate Verification Failed

**Error:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solution:**
Already fixed! The Apollo MCP client has `verify=False` set.

### SSL Warnings in Logs

**Warning:**
```
InsecureRequestWarning: Unverified HTTPS request is being made
```

**Solution:**
Already suppressed! Warnings are filtered in the code.

### Connection Still Fails

If you still get connection errors after SSL is disabled:

1. **Check Network Access:**
   ```bash
   curl -k https://uxl-mcp-mini-shop.uxl-platform.dev.cld.marriott.com/mcp/tools
   ```

2. **Check Firewall:**
   - Corporate firewall may block external connections
   - VPN may be required

3. **Check DNS:**
   ```bash
   nslookup uxl-mcp-mini-shop.uxl-platform.dev.cld.marriott.com
   ```

4. **Check Server Status:**
   - Server may be down
   - Endpoint may have changed

## Alternative SSL Configuration Methods

### Method 1: Environment Variable (Python)
```bash
export PYTHONHTTPSVERIFY=0
# OR
export CURL_CA_BUNDLE=""
```

### Method 2: Requests Library
```python
import requests
requests.get(url, verify=False)
```

### Method 3: httpx with Custom Timeout
```python
import httpx
client = httpx.Client(
    verify=False,
    timeout=30.0,
    follow_redirects=True
)
```

## Current Implementation Details

### File: `/app/backend/mcp_servers/apollo_mcp_client.py`

```python
class ApolloMCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        
        # ✅ SSL verification disabled for dev servers
        self.client = httpx.Client(timeout=30.0, verify=False)
        
        # ✅ Warnings suppressed
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
```

### Why This Works

1. **`verify=False`** tells httpx to accept any SSL certificate
2. **Warnings filter** prevents log spam
3. **Timeout set** to prevent hanging connections
4. **Applies to all requests** made by this client

## FAQ

**Q: Do I need to set NODE_TLS_REJECT_UNAUTHORIZED?**
A: No. That's for Node.js. We use Python with httpx.

**Q: Is SSL disabled for all connections?**
A: Only for MCP server connections via apollo_mcp_client.py. Regular backend operations use standard SSL.

**Q: Will this work in production?**
A: Yes, but consider using proper certificates for production deployments.

**Q: Can I enable SSL verification?**
A: Yes, change `verify=False` to `verify=True` in apollo_mcp_client.py

**Q: What about mock MCP servers?**
A: Mock servers run locally (no SSL needed). This only affects remote MCP servers.

## Summary

✅ **SSL/TLS is already configured correctly**
- Python backend has `verify=False` set
- Warnings are suppressed
- Works with self-signed certificates
- No additional configuration needed

🔒 **For Production:**
- Consider enabling verification
- Use proper CA certificates
- Or provide custom CA bundle

---

**No action required** - SSL configuration is already set up for remote MCP server access!
