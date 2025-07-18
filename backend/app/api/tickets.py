from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user_tickets(user_id: str) -> List[Dict[str, Any]]:
    """Get tickets for a user"""
    # Return empty list for demo
    return []

@router.post("/")
async def create_ticket(ticket_data: Dict[str, Any]):
    """Create a new ticket"""
    return {"id": "demo-ticket-123", "message": "Ticket created"}