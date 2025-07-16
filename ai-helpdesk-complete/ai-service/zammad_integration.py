import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class ZammadIntegration:
    def __init__(self):
        self.base_url = os.getenv("ZAMMAD_URL", "http://zammad-nginx:8080")
        self.api_token = os.getenv("ZAMMAD_API_TOKEN", "demo_token")
        self.session = None
        
    async def initialize(self):
        """Initialize Zammad integration"""
        try:
            logger.info("Initializing Zammad integration...")
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self._test_connection()
            logger.info("Zammad integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Zammad integration: {str(e)}")
            # Don't raise exception to allow system to start

    async def _test_connection(self):
        """Test Zammad API connection"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/users/me") as response:
                if response.status == 200:
                    logger.info("Zammad API connection successful")
                else:
                    logger.warning(f"Zammad API test failed with status: {response.status}")
        except Exception as e:
            logger.warning(f"Zammad API test failed: {str(e)}")

    async def create_ticket(self, title: str, description: str, group: str, priority: str = "2 normal") -> Dict[str, Any]:
        """Create a new ticket in Zammad"""
        try:
            # Map priority to Zammad priority IDs
            priority_mapping = {
                "low": "1 low",
                "medium": "2 normal", 
                "high": "3 high",
                "urgent": "3 high"
            }
            
            # Map group names to Zammad group names
            group_mapping = {
                "IT": "IT Support",
                "HR": "HR Support", 
                "Finance": "Finance",
                "Facilities": "Facilities",
                "General": "Support"
            }
            
            ticket_data = {
                "title": title,
                "group": group_mapping.get(group, "Support"),
                "priority": priority_mapping.get(priority, "2 normal"),
                "state": "new",
                "customer": "helpdesk-ai@company.com",
                "article": {
                    "subject": title,
                    "body": description,
                    "type": "note",
                    "internal": False
                }
            }
            
            if self.session is None:
                logger.warning("Zammad session not initialized, returning mock ticket")
                return {
                    "id": "mock_123",
                    "title": title,
                    "state": "new",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/tickets",
                json=ticket_data
            ) as response:
                if response.status == 201:
                    ticket = await response.json()
                    logger.info(f"Created Zammad ticket: {ticket.get('id')}")
                    return ticket
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create Zammad ticket: {response.status} - {error_text}")
                    return {"error": f"Failed to create ticket: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error creating Zammad ticket: {str(e)}")
            return {"error": str(e)}

    async def get_tickets(self, skip: int = 0, limit: int = 10, state: Optional[str] = None, group: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tickets from Zammad"""
        try:
            params = {
                "page": skip // limit + 1,
                "per_page": limit
            }
            
            if self.session is None:
                logger.warning("Zammad session not initialized, returning mock tickets")
                return [
                    {
                        "id": 1,
                        "title": "Sample IT Ticket",
                        "state": "open",
                        "group": "IT Support",
                        "priority": "2 normal",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            
            async with self.session.get(
                f"{self.base_url}/api/v1/tickets",
                params=params
            ) as response:
                if response.status == 200:
                    tickets = await response.json()
                    logger.info(f"Retrieved {len(tickets)} tickets from Zammad")
                    return tickets
                else:
                    logger.error(f"Failed to get Zammad tickets: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting Zammad tickets: {str(e)}")
            return []

    async def get_statistics(self) -> Dict[str, Any]:
        """Get Zammad statistics"""
        try:
            if self.session is None:
                return {
                    "total_tickets": 0,
                    "open_tickets": 0,
                    "closed_tickets": 0,
                    "groups": {}
                }
            
            # Get ticket stats (simplified)
            stats = {
                "total_tickets": 0,
                "open_tickets": 0, 
                "closed_tickets": 0,
                "groups": {
                    "IT Support": 0,
                    "HR Support": 0,
                    "Finance": 0,
                    "Facilities": 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting Zammad statistics: {str(e)}")
            return {}

    async def close(self):
        """Close Zammad integration"""
        if self.session:
            await self.session.close()