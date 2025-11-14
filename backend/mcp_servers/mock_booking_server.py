"""Mock MCP Booking Server for Hotel Booking Operations"""
import json
from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone
import random

class MockBookingServer:
    """Mock implementation of hotel booking MCP server"""
    
    def __init__(self):
        self.bookings = {}
        self.availability_cache = {}
    
    def check_availability(self, hotel_id: str, check_in: str, check_out: str, rooms: int = 1, room_type: str = "standard") -> Dict[str, Any]:
        """Check room availability for specific dates"""
        # Ensure rooms is at least 1
        rooms = rooms if rooms and rooms > 0 else 1
        
        # Simulate availability check
        is_available = random.choice([True, True, True, False])  # 75% available
        
        if not is_available:
            return {
                "success": True,
                "available": False,
                "message": "No rooms available for selected dates",
                "hotel_id": hotel_id
            }
        
        available_rooms = random.randint(1, 10)
        price_per_night = random.randint(100, 500)
        total_nights = self._calculate_nights(check_in, check_out)
        
        return {
            "success": True,
            "available": True,
            "hotel_id": hotel_id,
            "room_type": room_type,
            "available_rooms": available_rooms,
            "price_per_night": price_per_night,
            "total_nights": total_nights,
            "total_price": price_per_night * total_nights * rooms,
            "check_in": check_in,
            "check_out": check_out
        }
    
    def create_booking(self, hotel_id: str, check_in: str, check_out: str, guest_name: str, guest_email: str, rooms: int = 1, room_type: str = "standard") -> Dict[str, Any]:
        """Create a new booking"""
        # Ensure rooms is at least 1
        rooms = rooms if rooms and rooms > 0 else 1
        
        booking_id = f"booking_{uuid.uuid4().hex[:8]}"
        
        price_per_night = random.randint(100, 500)
        total_nights = self._calculate_nights(check_in, check_out)
        
        booking = {
            "booking_id": booking_id,
            "hotel_id": hotel_id,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "check_in": check_in,
            "check_out": check_out,
            "rooms": rooms,
            "room_type": room_type,
            "price_per_night": price_per_night,
            "total_nights": total_nights,
            "total_price": price_per_night * total_nights * rooms,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.bookings[booking_id] = booking
        
        return {
            "success": True,
            "booking": booking,
            "message": "Booking created successfully. Please confirm to complete."
        }
    
    def confirm_booking(self, booking_id: str, payment_method: str = "credit_card") -> Dict[str, Any]:
        """Confirm and finalize a booking"""
        if booking_id not in self.bookings:
            return {
                "success": False,
                "error": "Booking not found"
            }
        
        booking = self.bookings[booking_id]
        
        if booking['status'] == 'confirmed':
            return {
                "success": False,
                "error": "Booking already confirmed"
            }
        
        booking['status'] = 'confirmed'
        booking['payment_method'] = payment_method
        booking['confirmation_number'] = f"CONF{uuid.uuid4().hex[:6].upper()}"
        booking['confirmed_at'] = datetime.now(timezone.utc).isoformat()
        
        return {
            "success": True,
            "booking": booking,
            "message": f"Booking confirmed! Confirmation number: {booking['confirmation_number']}"
        }
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking"""
        if booking_id not in self.bookings:
            return {
                "success": False,
                "error": "Booking not found"
            }
        
        booking = self.bookings[booking_id]
        booking['status'] = 'cancelled'
        booking['cancelled_at'] = datetime.now(timezone.utc).isoformat()
        
        return {
            "success": True,
            "booking": booking,
            "message": "Booking cancelled successfully"
        }
    
    def get_booking_details(self, booking_id: str) -> Dict[str, Any]:
        """Get details of a specific booking"""
        if booking_id not in self.bookings:
            return {
                "success": False,
                "error": "Booking not found"
            }
        
        return {
            "success": True,
            "booking": self.bookings[booking_id]
        }
    
    def _calculate_nights(self, check_in: str, check_out: str) -> int:
        """Calculate number of nights between dates"""
        if not check_in or not check_out:
            return 1
        try:
            # Handle various date formats
            if 'T' in check_in:
                start = datetime.fromisoformat(check_in.replace('Z', '+00:00'))
            else:
                start = datetime.strptime(check_in, '%Y-%m-%d')
            
            if 'T' in check_out:
                end = datetime.fromisoformat(check_out.replace('Z', '+00:00'))
            else:
                end = datetime.strptime(check_out, '%Y-%m-%d')
            
            return max(1, (end - start).days)
        except Exception as e:
            return 1
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools in this MCP server"""
        return [
            {
                "name": "check_availability",
                "description": "Check room availability for specific dates",
                "parameters": {
                    "hotel_id": "string (required)",
                    "check_in": "string YYYY-MM-DD (required)",
                    "check_out": "string YYYY-MM-DD (required)",
                    "rooms": "integer (optional, default: 1)",
                    "room_type": "string (optional, default: 'standard')"
                }
            },
            {
                "name": "create_booking",
                "description": "Create a new hotel booking",
                "parameters": {
                    "hotel_id": "string (required)",
                    "check_in": "string YYYY-MM-DD (required)",
                    "check_out": "string YYYY-MM-DD (required)",
                    "guest_name": "string (required)",
                    "guest_email": "string (required)",
                    "rooms": "integer (optional, default: 1)",
                    "room_type": "string (optional, default: 'standard')"
                }
            },
            {
                "name": "confirm_booking",
                "description": "Confirm and finalize a booking",
                "parameters": {
                    "booking_id": "string (required)",
                    "payment_method": "string (optional, default: 'credit_card')"
                }
            },
            {
                "name": "cancel_booking",
                "description": "Cancel an existing booking",
                "parameters": {
                    "booking_id": "string (required)"
                }
            },
            {
                "name": "get_booking_details",
                "description": "Get details of a specific booking",
                "parameters": {
                    "booking_id": "string (required)"
                }
            }
        ]

# Singleton instance
booking_server = MockBookingServer()