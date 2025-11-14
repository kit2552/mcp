"""Apollo GraphQL MCP Server Client"""
import httpx
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ApolloMCPClient:
    """Client for Apollo GraphQL MCP Server using HTTP Streaming"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        # Disable SSL verification for internal/dev servers
        self.client = httpx.Client(timeout=30.0, verify=False)
        self.tools_cache = None
        self.session_initialized = False
        self.server_capabilities = {}
        self.request_id_counter = 0
        
        # Suppress SSL warnings
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        # Initialize the MCP session
        self._initialize_session()
    
    def _send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC message via HTTP streaming to MCP server"""
        try:
            # All messages go to root endpoint (not /execute)
            url = self.server_url
            
            # MCP uses HTTP streaming protocol
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"Sending message to {url}: {message}")
            
            # Send as streaming POST
            with self.client.stream("POST", url, json=message, headers=headers) as response:
                response.raise_for_status()
                
                # Read streaming response
                result = None
                for line in response.iter_lines():
                    if line.strip():
                        try:
                            result = json.loads(line)
                            logger.info(f"Received: {result}")
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse line: {line}")
                            continue
                
                if result:
                    return result
                else:
                    return {"success": False, "error": "No response from server"}
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error connecting to MCP server: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return {"success": False, "error": str(e), "status_code": e.response.status_code if hasattr(e, 'response') else None}
        except httpx.HTTPError as e:
            logger.error(f"HTTP error connecting to MCP server: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending message to MCP server: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_session(self):
        """Initialize MCP session with the server"""
        try:
            self.request_id_counter += 1
            
            # MCP initialize request
            message = {
                "jsonrpc": "2.0",
                "id": self.request_id_counter,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        }
                    },
                    "clientInfo": {
                        "name": "ai-hotel-assistant",
                        "version": "1.0.0"
                    }
                }
            }
            
            logger.info(f"Initializing MCP session with server: {self.server_url}")
            
            # Send initialize message via HTTP streaming
            result = self._send_message(message)
            
            if isinstance(result, dict) and "result" in result:
                self.session_initialized = True
                self.server_capabilities = result.get("result", {}).get("capabilities", {})
                logger.info(f"✅ MCP session initialized successfully!")
                logger.info(f"Server capabilities: {self.server_capabilities}")
            else:
                logger.warning(f"⚠️ MCP initialization did not return expected result: {result}")
                logger.warning("Will continue with mock data fallback")
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP session: {e}")
            # Don't raise - we'll fall back to mock data
    
    def _parse_sse_response(self, sse_text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events (SSE) response"""
        try:
            # SSE format: data: {...}\n\n
            lines = sse_text.strip().split('\n')
            result_data = {}
            
            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    try:
                        result_data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
            
            if result_data:
                return result_data
            else:
                return {"success": False, "error": "No valid data in SSE stream"}
        
        except Exception as e:
            logger.error(f"Error parsing SSE response: {e}")
            return {"success": False, "error": f"SSE parse error: {str(e)}"}
    
    def _try_graphql_query(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Try calling tool via GraphQL query format"""
        try:
            # Build GraphQL query based on tool
            if tool_name == "get_property":
                query = """
                query GetProperty($propertyId: String!) {
                    getProperty(propertyId: $propertyId) {
                        id
                        name
                        location
                        amenities
                        rating
                    }
                }
                """
            elif tool_name == "searchrates":
                query = """
                query SearchRates($city: String!, $checkIn: String, $checkOut: String, $guests: Int, $brands: [String]) {
                    searchRates(city: $city, checkIn: $checkIn, checkOut: $checkOut, guests: $guests, brands: $brands) {
                        properties {
                            id
                            name
                            city
                            rate
                        }
                    }
                }
                """
            elif tool_name == "marketing":
                query = """
                query GetMarketing($propertyId: String!) {
                    getMarketing(propertyId: $propertyId) {
                        offers
                        promotions
                    }
                }
                """
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
            payload = {
                "query": query,
                "variables": parameters
            }
            
            # Try root endpoint for GraphQL
            result = self._make_request("", method="POST", data=payload)
            return result
            
        except Exception as e:
            logger.error(f"GraphQL query error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server"""
        if self.tools_cache:
            return self.tools_cache
        
        try:
            # Try to fetch tools schema from MCP server
            result = self._make_request("tools", method="GET")
            
            if result.get("success") == False:
                logger.warning("Could not fetch tools from MCP server, using default schema")
                # Return default tool definitions for the Marriott MCP server
                self.tools_cache = [
                    {
                        "name": "get_property",
                        "description": "Get property details by property ID",
                        "parameters": {
                            "propertyId": "string (required) - The unique identifier for the property"
                        }
                    },
                    {
                        "name": "searchrates",
                        "description": "Search for hotels in a city with dates, guests, and brands",
                        "parameters": {
                            "city": "string (required) - City name to search in",
                            "checkIn": "string (required) - Check-in date in YYYY-MM-DD format",
                            "checkOut": "string (required) - Check-out date in YYYY-MM-DD format",
                            "guests": "integer (optional) - Number of guests",
                            "brands": "array of strings (optional) - Hotel brands to filter"
                        }
                    },
                    {
                        "name": "marketing",
                        "description": "Get marketing offers and promotions available at a property",
                        "parameters": {
                            "propertyId": "string (required) - The unique identifier for the property"
                        }
                    }
                ]
            else:
                self.tools_cache = result.get("tools", [])
            
            return self.tools_cache
        
        except Exception as e:
            logger.error(f"Error fetching tools: {e}")
            return []
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server"""
        try:
            # MCP server uses JSON-RPC 2.0 protocol
            # Generate unique request ID
            import time
            request_id = int(time.time() * 1000)
            
            # JSON-RPC 2.0 format
            payload = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            logger.info(f"Calling tool {tool_name} with JSON-RPC payload: {payload}")
            
            result = self._make_request("execute", method="POST", data=payload)
            
            # Handle error responses
            if isinstance(result, dict):
                # Check for JSON-RPC error response
                if "error" in result:
                    error_msg = result["error"].get("message", str(result["error"])) if isinstance(result["error"], dict) else str(result["error"])
                    logger.error(f"JSON-RPC error: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
                
                # Extract result from JSON-RPC response
                if "result" in result:
                    return result["result"]
                
                return result
            else:
                # Non-dict response (error string)
                logger.error(f"Unexpected response type: {type(result)}")
                return {
                    "success": False,
                    "error": str(result)
                }
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_properties(self, city: str = None, check_in: str = None, check_out: str = None, 
                         guests: int = 1, brands: List[str] = None) -> Dict[str, Any]:
        """Search for properties using searchrates tool"""
        parameters = {}
        
        if city:
            parameters["city"] = city
        if check_in:
            parameters["checkIn"] = check_in
        if check_out:
            parameters["checkOut"] = check_out
        if guests:
            parameters["guests"] = guests
        if brands:
            parameters["brands"] = brands
        
        result = self.call_tool("searchrates", parameters)
        
        # If remote call fails, return mock data
        if not result.get("success", True) and result.get("status_code") in [406, 404, 500]:
            logger.warning(f"Remote MCP server failed, returning mock search results for {city}")
            return {
                "success": True,
                "results": [
                    {
                        "id": f"{city}_hotel_1",
                        "name": f"Marriott {city} Hotel",
                        "city": city or "Unknown",
                        "rating": 4.5,
                        "rate": 199,
                        "amenities": ["WiFi", "Pool", "Gym"]
                    },
                    {
                        "id": f"{city}_hotel_2",
                        "name": f"Sheraton {city} Hotel",
                        "city": city or "Unknown",
                        "rating": 4.3,
                        "rate": 179,
                        "amenities": ["WiFi", "Restaurant", "Bar"]
                    }
                ],
                "total_count": 2,
                "note": "This is mock data - remote MCP server connection failed"
            }
        
        return result
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details using get_property tool"""
        result = self.call_tool("get_property", {"propertyId": property_id})
        
        # If remote call fails, return mock data for testing
        if not result.get("success", True) and result.get("status_code") in [406, 404, 500]:
            logger.warning(f"Remote MCP server failed, returning mock data for property {property_id}")
            return {
                "success": True,
                "property": {
                    "id": property_id,
                    "name": f"Property {property_id}",
                    "location": "New York, NY",
                    "rating": 4.5,
                    "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                    "description": "A wonderful property in a great location",
                    "note": "This is mock data - remote MCP server connection failed"
                }
            }
        
        return result
    
    def get_property_offers(self, property_id: str) -> Dict[str, Any]:
        """Get property marketing offers using marketing tool"""
        return self.call_tool("marketing", {"propertyId": property_id})
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()