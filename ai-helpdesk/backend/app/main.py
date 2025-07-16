from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from .config import settings
from .api import chat, tickets, knowledge
from .services.llm_service import LLMService
from .services.rag_service import RAGService
from .models import Base
from .database import engine

# Initialize services
llm_service = LLMService()
rag_service = RAGService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    await llm_service.initialize()
    await rag_service.initialize()
    yield
    # Shutdown
    await llm_service.cleanup()
    await rag_service.cleanup()

app = FastAPI(
    title="AI Helpdesk API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])

@app.get("/")
async def root():
    return {"message": "AI Helpdesk API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "qdrant": "connected",
            "ollama": "connected"
        }
    }