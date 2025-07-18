import httpx
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import settings
import json

class TicketService:
    def __init__(self):
        self.zammad_url = "http://zammad:80/api/v1"
        self.zammad_token = settings.ZAMMAD_TOKEN if hasattr(settings, 'ZAMMAD_TOKEN') else None
        # For initial setup, use basic auth
        self.zammad_user = "admin@example.com"
        self.zammad_password = "admin123"
        
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create ticket in Zammad"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use basic auth if no token
        auth = None
        if self.zammad_token:
            headers["Authorization"] = f"Token token={self.zammad_token}"
        else:
            auth = (self.zammad_user, self.zammad_password)
        
        zammad_ticket = {
            "title": ticket_data["title"],
            "group": "Users",  # Default group
            "customer_id": "guess:" + ticket_data.get("user_id", "user@example.com"),
            "article": {
                "subject": ticket_data["title"],
                "body": ticket_data["description"],
                "type": "note",
                "internal": False
            },
            "state_id": 1,  # new
            "priority_id": 2  # normal
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.zammad_url}/tickets",
                    headers=headers,
                    json=zammad_ticket,
                    auth=auth,
                    timeout=30.0
                )
                if response.status_code == 201:
                    ticket = response.json()
                    return str(ticket.get("id", "error"))
                else:
                    print(f"Zammad error: {response.status_code} - {response.text}")
                    # Fallback to local ID
                    return f"local-{uuid.uuid4()}"
            except Exception as e:
                print(f"Error creating Zammad ticket: {e}")
                # Return local ID as fallback
                return f"local-{uuid.uuid4()}"
    
    async def search_tickets(self, query: str) -> List[Dict[str, Any]]:
        """Search existing tickets"""
        headers = {}
        auth = None
        
        if self.zammad_token:
            headers["Authorization"] = f"Token token={self.zammad_token}"
        else:
            auth = (self.zammad_user, self.zammad_password)
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.zammad_url}/tickets/search",
                    params={"query": query, "limit": 10},
                    headers=headers,
                    auth=auth,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json().get("assets", {}).get("Ticket", [])
                return []
            except Exception as e:
                print(f"Error searching tickets: {e}")
                return []