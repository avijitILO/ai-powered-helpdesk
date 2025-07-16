from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    department: str
    priority: str
    confidence: float
    suggested_actions: List[str]
    knowledge_articles: List[Dict[str, Any]]
    should_create_ticket: bool
    timestamp: datetime = datetime.utcnow()

class TicketCreateRequest(BaseModel):
    title: str
    description: str
    department: str
    priority: str = "medium"
    customer_email: Optional[str] = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None