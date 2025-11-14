"""Apollo GraphQL MCP Server Client"""
import httpx
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ApolloMCPClient:
    """Client for Apollo GraphQL MCP Server"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        # Disable SSL verification for internal/dev servers
        self.client = httpx.Client(timeout=30.0, verify=False)
        self.tools_cache = None
        
        # Suppress SSL warnings
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to MCP server"""
        try:
            url = f"{self.server_url}/{endpoint}"
            
            # Set proper headers for Apollo MCP server
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if method == "GET":
                response = self.client.get(url, headers=headers)
            elif method == "POST":
                response = self.client.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error connecting to MCP server: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return {"success": False, "error": str(e), "status_code": e.response.status_code if hasattr(e, 'response') else None}
        except httpx.HTTPError as e:
            logger.error(f"HTTP error connecting to MCP server: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error making request to MCP server: {e}")
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
            # Make GraphQL-style request to the tool
            payload = {
                "tool": tool_name,
                "parameters": parameters
            }
            
            result = self._make_request("execute", method="POST", data=payload)
            
            return result
        
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
        
        return self.call_tool("searchrates", parameters)
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details using get_property tool"""
        return self.call_tool("get_property", {"propertyId": property_id})
    
    def get_property_offers(self, property_id: str) -> Dict[str, Any]:
        """Get property marketing offers using marketing tool"""
        return self.call_tool("marketing", {"propertyId": property_id})
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()