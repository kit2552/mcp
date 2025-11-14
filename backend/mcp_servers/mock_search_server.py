"""Mock MCP Search Server for Hotel Search Operations"""
import json
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

class MockSearchServer:
    """Mock implementation of hotel search MCP server"""
    
    def __init__(self):
        self.hotels_db = self._generate_mock_hotels()
    
    def _generate_mock_hotels(self) -> List[Dict[str, Any]]:
        """Generate mock hotel data"""
        locations = ["New York", "Paris", "Tokyo", "London", "Dubai", "Singapore", "Barcelona", "Rome"]
        hotel_types = ["Luxury", "Business", "Boutique", "Resort", "Budget"]
        
        hotels = []
        for i in range(50):
            location = random.choice(locations)
            hotel_type = random.choice(hotel_types)
            hotels.append({
                "id": f"hotel_{i+1}",
                "name": f"{hotel_type} {location} Hotel {i+1}",
                "location": location,
                "type": hotel_type,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "price_per_night": random.randint(80, 800),
                "amenities": random.sample(["WiFi", "Pool", "Gym", "Restaurant", "Spa", "Bar", "Parking", "Room Service"], k=random.randint(3, 6)),
                "available_rooms": random.randint(5, 50),
                "description": f"A wonderful {hotel_type.lower()} hotel in {location}"
            })
        return hotels
    
    def search_hotels(self, location: str = None, check_in: str = None, check_out: str = None, guests: int = 1) -> Dict[str, Any]:
        """Search for hotels based on criteria"""
        filtered_hotels = self.hotels_db
        
        if location:
            filtered_hotels = [h for h in filtered_hotels if location.lower() in h['location'].lower()]
        
        return {
            "success": True,
            "results": filtered_hotels[:10],
            "total_count": len(filtered_hotels),
            "search_params": {
                "location": location,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests
            }
        }
    
    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific hotel"""
        hotel = next((h for h in self.hotels_db if h['id'] == hotel_id), None)
        
        if not hotel:
            return {"success": False, "error": "Hotel not found"}
        
        return {
            "success": True,
            "hotel": hotel
        }
    
    def filter_hotels(self, min_rating: float = None, max_price: int = None, amenities: List[str] = None, hotel_type: str = None) -> Dict[str, Any]:
        """Filter hotels by specific criteria"""
        filtered = self.hotels_db
        
        if min_rating:
            filtered = [h for h in filtered if h['rating'] >= min_rating]
        
        if max_price:
            filtered = [h for h in filtered if h['price_per_night'] <= max_price]
        
        if amenities:
            filtered = [h for h in filtered if any(a in h['amenities'] for a in amenities)]
        
        if hotel_type:
            filtered = [h for h in filtered if hotel_type.lower() in h['type'].lower()]
        
        return {
            "success": True,
            "results": filtered[:15],
            "filters_applied": {
                "min_rating": min_rating,
                "max_price": max_price,
                "amenities": amenities,
                "hotel_type": hotel_type
            }
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools in this MCP server"""
        return [
            {
                "name": "search_hotels",
                "description": "Search for hotels by location, dates, and guest count",
                "parameters": {
                    "location": "string (optional)",
                    "check_in": "string YYYY-MM-DD (optional)",
                    "check_out": "string YYYY-MM-DD (optional)",
                    "guests": "integer (optional, default: 1)"
                }
            },
            {
                "name": "get_hotel_details",
                "description": "Get detailed information about a specific hotel",
                "parameters": {
                    "hotel_id": "string (required)"
                }
            },
            {
                "name": "filter_hotels",
                "description": "Filter hotels by rating, price, amenities, and type",
                "parameters": {
                    "min_rating": "float (optional)",
                    "max_price": "integer (optional)",
                    "amenities": "list of strings (optional)",
                    "hotel_type": "string (optional)"
                }
            }
        ]

# Singleton instance
search_server = MockSearchServer()