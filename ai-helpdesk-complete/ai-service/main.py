from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from database import engine, get_db
from models import Base
from schemas import ChatRequest, ChatResponse, TicketCreateRequest, KnowledgeSearchRequest
from ai_processor import AIProcessor
from zammad_integration import ZammadIntegration
from bookstack_integration import BookStackIntegration
from vector_service import VectorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ai-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize services
ai_processor = AIProcessor()
zammad_integration = ZammadIntegration()
bookstack_integration = BookStackIntegration()
vector_service = VectorService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Helpdesk Service...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize services
    await ai_processor.initialize()
    await vector_service.initialize()
    await zammad_integration.initialize()
    await bookstack_integration.initialize()
    
    logger.info("AI Helpdesk Service started successfully!")
    yield
    logger.info("Shutting down AI Helpdesk Service...")

app = FastAPI(
    title="AI Helpdesk Service",
    description="AI-powered helpdesk integration with Zammad and BookStack",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "ai_processor": "operational",
            "vector_service": "operational",
            "zammad": "operational",
            "bookstack": "operational"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Main chat endpoint for AI assistance"""
    try:
        # Process message with AI
        ai_response = await ai_processor.process_message(request.message, db)
        
        # Search knowledge base for relevant articles
        kb_results = await bookstack_integration.search_articles(request.message)
        
        # Determine if ticket should be created
        if ai_response.should_create_ticket:
            background_tasks.add_task(
                create_ticket_from_chat,
                request.message,
                ai_response.department,
                ai_response.priority
            )
        
        return ChatResponse(
            message=ai_response.response,
            department=ai_response.department,
            priority=ai_response.priority,
            confidence=ai_response.confidence,
            suggested_actions=ai_response.suggested_actions,
            knowledge_articles=kb_results[:3],
            should_create_ticket=ai_response.should_create_ticket
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/tickets")
async def create_ticket(request: TicketCreateRequest):
    """Create a new ticket in Zammad"""
    try:
        ticket = await zammad_integration.create_ticket(
            title=request.title,
            description=request.description,
            group=request.department,
            priority=request.priority
        )
        return ticket
    except Exception as e:
        logger.error(f"Ticket creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")

@app.get("/tickets")
async def get_tickets(
    skip: int = 0,
    limit: int = 10,
    state: Optional[str] = None,
    group: Optional[str] = None
):
    """Get tickets from Zammad"""
    try:
        tickets = await zammad_integration.get_tickets(
            skip=skip,
            limit=limit,
            state=state,
            group=group
        )
        return tickets
    except Exception as e:
        logger.error(f"Error fetching tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tickets")

@app.post("/knowledge/search")
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search knowledge base"""
    try:
        # Search in BookStack
        bookstack_results = await bookstack_integration.search_articles(request.query)
        
        # Search in vector database for AI-enhanced results
        vector_results = await vector_service.similarity_search(request.query, limit=5)
        
        return {
            "bookstack_results": bookstack_results,
            "ai_enhanced_results": vector_results
        }
    except Exception as e:
        logger.error(f"Knowledge search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")

@app.post("/knowledge/sync")
async def sync_knowledge_base():
    """Sync knowledge base from BookStack to vector database"""
    try:
        # Get all articles from BookStack
        articles = await bookstack_integration.get_all_articles()
        
        # Add to vector database
        for article in articles:
            await vector_service.add_document(
                content=f"{article['name']}\n{article['text']}",
                metadata={
                    "source": "bookstack",
                    "article_id": article["id"],
                    "title": article["name"],
                    "url": article["url"]
                }
            )
        
        return {"message": f"Synced {len(articles)} articles to vector database"}
    except Exception as e:
        logger.error(f"Knowledge sync error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync knowledge base")

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        zammad_stats = await zammad_integration.get_statistics()
        bookstack_stats = await bookstack_integration.get_statistics()
        
        return {
            "tickets": zammad_stats,
            "knowledge_base": bookstack_stats,
            "ai_interactions": await ai_processor.get_interaction_stats()
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

# Background task functions
async def create_ticket_from_chat(message: str, department: str, priority: str):
    """Create ticket from chat interaction"""
    try:
        ticket = await zammad_integration.create_ticket(
        title=f"AI Chat Support: {message[:50]}...",
        description=f"User inquiry: {message}",
        group=department,
        priority=priority)
        logger.info(f"Created ticket from chat: {ticket.get('id')}")
    except Exception as e:
        logger.error(f"Error creating ticket from chat: {str(e)}")
        if name == "main":import uvicorn 
        uvicorn.run(app, host="0.0.0.0", port=8000)