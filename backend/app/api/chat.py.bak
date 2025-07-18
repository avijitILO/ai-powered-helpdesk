from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..services.llm_service import LLMService
from ..services.rag_service import RAGService
from ..services.ticket_service import TicketService

router = APIRouter()

# Initialize services
llm_service = LLMService()
rag_service = RAGService()
ticket_service = TicketService()

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
    """Process chat message and return AI response"""
    try:
        # Get relevant context from RAG
        context = await rag_service.get_context(request.message)
        
        # Generate response
        response = await llm_service.generate_response(
            request.message,
            context
        )
        
        # Classify department
        department = await llm_service.classify_department(request.message)
        
        # Create ticket if needed (based on keywords or sentiment)
        ticket_id = None
        if any(keyword in request.message.lower() for keyword in ["help", "issue", "problem", "error", "urgent"]):
            ticket_id = await ticket_service.create_ticket({
                "title": f"Query: {request.message[:50]}...",
                "description": request.message,
                "department": department,
                "user_id": request.user_id,
                "priority": "normal",
                "status": "open"
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    message_id: str,
    helpful: bool,
    feedback: Optional[str] = None
):
    """Submit feedback for a chat response"""
    # Store feedback for model improvement
    return {"status": "feedback received"}