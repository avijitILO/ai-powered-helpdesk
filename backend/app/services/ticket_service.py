import httpx
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.ticket import Ticket, TicketStatus, TicketPriority
from ..database import get_db
from ..config import settings
import json

class TicketService:
    def __init__(self):
        self.zammad_url = settings.ZAMMAD_URL if hasattr(settings, 'ZAMMAD_URL') else None
        self.zammad_token = settings.ZAMMAD_TOKEN if hasattr(settings, 'ZAMMAD_TOKEN') else None
        
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a new ticket in local DB"""
        ticket_id = str(uuid.uuid4())
        
        db = next(get_db())
        try:
            db_ticket = Ticket(
                id=ticket_id,
                title=ticket_data["title"],
                description=ticket_data["description"],
                department=ticket_data["department"],
                user_id=ticket_data["user_id"],
                status=ticket_data.get("status", "open"),
                priority=ticket_data.get("priority", "normal")
            )
            db.add(db_ticket)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
        return ticket_id
    
    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by ID"""
        db = next(get_db())
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                return {
                    "id": ticket.id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "department": ticket.department,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "created_at": ticket.created_at.isoformat()
                }
            return None
        finally:
            db.close()
    
    async def get_user_tickets(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tickets for a specific user"""
        # Return empty list for now if database not ready
        return []