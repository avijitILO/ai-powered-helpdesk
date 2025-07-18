from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..services.llm_service import LLMService
from ..services.rag_service import RAGService
from ..services.ticket_service import TicketService
from ..services.knowledge_service import KnowledgeService

router = APIRouter()

# Initialize services
llm_service = LLMService()
rag_service = RAGService()
ticket_service = TicketService()
knowledge_service = KnowledgeService()

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    department: str
    ticket_id: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with ticket creation"""
    try:
        # Search for relevant knowledge
        context = await rag_service.get_context(request.message)
        
        # Generate response (simple for now)
        response = f"I understand you need help with: {request.message}. Based on our knowledge base, here's what I found: {context[:200]}..."
        
        # Classify department
        message_lower = request.message.lower()
        if any(word in message_lower for word in ["password", "login", "email", "vpn", "computer"]):
            department = "IT"
        elif any(word in message_lower for word in ["leave", "vacation", "hr", "employee"]):
            department = "HR"
        elif any(word in message_lower for word in ["expense", "payroll", "salary", "invoice"]):
            department = "Finance"
        else:
            department = "General"
        
        # Create ticket if it's an issue/request
        ticket_id = None
        if any(word in message_lower for word in ["help", "issue", "problem", "not working", "error", "can't", "cannot"]):
            ticket_id = await ticket_service.create_ticket({
                "title": f"Query: {request.message[:50]}...",
                "description": request.message,
                "department": department,
                "user_id": request.user_id
            })
        
        # Get sources
        sources = await rag_service.search_documents(request.message, limit=3)
        
        return ChatResponse(
            response=response,
            department=department,
            ticket_id=ticket_id,
            sources=sources
        )
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    ticket_id: str,
    resolved: bool,
    resolution: Optional[str] = None
):
    """Convert resolved ticket to knowledge base article"""
    if resolved and resolution:
        # Create KB article from resolution
        await knowledge_service.create_article({
            "title": f"Resolution for Ticket {ticket_id}",
            "content": resolution,
            "category": "Ticket Resolution",
            "department": "General"
        })
        return {"message": "Feedback received and KB updated"}
    return {"message": "Feedback received"}