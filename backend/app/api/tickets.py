from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter()

class TicketCreate(BaseModel):
    title: str
    description: str
    department: str
    user_id: str
    priority: Optional[str] = "normal"

class TicketResponse(BaseModel):
    id: str
    title: str
    status: str
    created_at: str

@router.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(user_id: str):
    """Get tickets for a user"""
    return []

@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    """Create a new ticket"""
    return TicketResponse(
        id="demo-123",
        title=ticket.title,
        status="open",
        created_at="2024-01-15T10:00:00Z"
    )