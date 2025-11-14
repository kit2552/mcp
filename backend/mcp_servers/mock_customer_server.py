"""Mock MCP Customer Server for Customer Data Operations"""
import json
from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone, timedelta
import random

class MockCustomerServer:
    """Mock implementation of customer data MCP server"""
    
    def __init__(self):
        self.customers = self._generate_mock_customers()
        self.trips = self._generate_mock_trips()
        self.rewards = self._generate_mock_rewards()
    
    def _generate_mock_customers(self) -> Dict[str, Any]:
        """Generate mock customer profiles"""
        return {
            "customer_1": {
                "customer_id": "customer_1",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "loyalty_tier": "Gold",
                "member_since": "2020-01-15",
                "preferences": {
                    "room_type": "King Suite",
                    "floor_preference": "High floor",
                    "amenities": ["WiFi", "Gym", "Pool"],
                    "special_requests": "Extra pillows"
                },
                "total_bookings": 24,
                "total_spent": 12500.00
            },
            "customer_2": {
                "customer_id": "customer_2",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-0124",
                "loyalty_tier": "Platinum",
                "member_since": "2019-03-20",
                "preferences": {
                    "room_type": "Ocean View",
                    "floor_preference": "Any",
                    "amenities": ["Spa", "Restaurant", "Bar"],
                    "special_requests": "Late checkout"
                },
                "total_bookings": 45,
                "total_spent": 28000.00
            }
        }
    
    def _generate_mock_trips(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mock customer trips"""
        return {
            "customer_1": [
                {
                    "trip_id": "trip_001",
                    "hotel_name": "Luxury Paris Hotel",
                    "location": "Paris, France",
                    "check_in": "2024-06-15",
                    "check_out": "2024-06-20",
                    "status": "completed",
                    "total_cost": 1500.00,
                    "rating_given": 5
                },
                {
                    "trip_id": "trip_002",
                    "hotel_name": "Business Tokyo Hotel",
                    "location": "Tokyo, Japan",
                    "check_in": "2024-09-10",
                    "check_out": "2024-09-15",
                    "status": "completed",
                    "total_cost": 2200.00,
                    "rating_given": 4
                },
                {
                    "trip_id": "trip_003",
                    "hotel_name": "Resort Dubai Hotel",
                    "location": "Dubai, UAE",
                    "check_in": "2025-02-01",
                    "check_out": "2025-02-07",
                    "status": "upcoming",
                    "total_cost": 3500.00,
                    "rating_given": None
                }
            ],
            "customer_2": [
                {
                    "trip_id": "trip_101",
                    "hotel_name": "Boutique London Hotel",
                    "location": "London, UK",
                    "check_in": "2024-08-01",
                    "check_out": "2024-08-05",
                    "status": "completed",
                    "total_cost": 1800.00,
                    "rating_given": 5
                }
            ]
        }
    
    def _generate_mock_rewards(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock customer rewards"""
        return {
            "customer_1": {
                "customer_id": "customer_1",
                "points_balance": 8500,
                "points_earned_ytd": 12000,
                "points_redeemed_ytd": 3500,
                "tier": "Gold",
                "tier_benefits": [
                    "Free breakfast",
                    "Room upgrade (subject to availability)",
                    "Late checkout",
                    "10% bonus points"
                ],
                "vouchers": [
                    {
                        "voucher_id": "VOUCHER_001",
                        "type": "Discount",
                        "value": 50.00,
                        "expires": "2025-12-31"
                    },
                    {
                        "voucher_id": "VOUCHER_002",
                        "type": "Free Night",
                        "value": "1 night",
                        "expires": "2025-06-30"
                    }
                ],
                "next_tier": "Platinum",
                "points_to_next_tier": 1500
            },
            "customer_2": {
                "customer_id": "customer_2",
                "points_balance": 15000,
                "points_earned_ytd": 22000,
                "points_redeemed_ytd": 7000,
                "tier": "Platinum",
                "tier_benefits": [
                    "Free breakfast",
                    "Guaranteed room upgrade",
                    "Late checkout until 4 PM",
                    "20% bonus points",
                    "Airport lounge access"
                ],
                "vouchers": [
                    {
                        "voucher_id": "VOUCHER_101",
                        "type": "Discount",
                        "value": 100.00,
                        "expires": "2025-12-31"
                    }
                ],
                "next_tier": "Diamond",
                "points_to_next_tier": 5000
            }
        }
    
    def get_customer_profile(self, customer_id: str = None, email: str = None) -> Dict[str, Any]:
        """Get customer profile information"""
        # Search by customer_id or email
        customer = None
        
        if customer_id and customer_id in self.customers:
            customer = self.customers[customer_id]
        elif email:
            for cust in self.customers.values():
                if cust['email'].lower() == email.lower():
                    customer = cust
                    break
        
        if not customer:
            return {
                "success": False,
                "error": "Customer not found"
            }
        
        return {
            "success": True,
            "profile": customer
        }
    
    def get_customer_trips(self, customer_id: str, status: str = None) -> Dict[str, Any]:
        """Get customer trip history"""
        if customer_id not in self.trips:
            return {
                "success": False,
                "error": "No trips found for customer"
            }
        
        trips = self.trips[customer_id]
        
        # Filter by status if provided
        if status:
            trips = [t for t in trips if t['status'] == status]
        
        return {
            "success": True,
            "customer_id": customer_id,
            "trips": trips,
            "total_trips": len(trips)
        }
    
    def get_customer_rewards(self, customer_id: str) -> Dict[str, Any]:
        """Get customer rewards and loyalty information"""
        if customer_id not in self.rewards:
            return {
                "success": False,
                "error": "No rewards found for customer"
            }
        
        rewards = self.rewards[customer_id]
        
        return {
            "success": True,
            "rewards": rewards
        }
    
    def update_customer_profile(self, customer_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer profile information"""
        if customer_id not in self.customers:
            return {
                "success": False,
                "error": "Customer not found"
            }
        
        customer = self.customers[customer_id]
        
        # Update allowed fields
        allowed_fields = ['phone', 'preferences']
        for field in allowed_fields:
            if field in updates:
                if field == 'preferences' and isinstance(updates[field], dict):
                    # Merge preferences
                    customer['preferences'].update(updates[field])
                else:
                    customer[field] = updates[field]
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": customer
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools in this MCP server"""
        return [
            {
                "name": "get_customer_profile",
                "description": "Get customer profile information by customer_id or email",
                "parameters": {
                    "customer_id": "string (optional)",
                    "email": "string (optional)"
                }
            },
            {
                "name": "get_customer_trips",
                "description": "Get customer trip history, optionally filtered by status",
                "parameters": {
                    "customer_id": "string (required)",
                    "status": "string (optional: 'completed', 'upcoming', 'cancelled')"
                }
            },
            {
                "name": "get_customer_rewards",
                "description": "Get customer rewards, loyalty points, tier, and vouchers",
                "parameters": {
                    "customer_id": "string (required)"
                }
            },
            {
                "name": "update_customer_profile",
                "description": "Update customer profile information (phone, preferences)",
                "parameters": {
                    "customer_id": "string (required)",
                    "updates": "object with fields to update"
                }
            }
        ]

# Singleton instance
customer_server = MockCustomerServer()