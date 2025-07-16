from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from database import Base

class ChatInteraction(Base):
    __tablename__ = "chat_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    department = Column(String(50), nullable=True)
    priority = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    created_ticket = Column(Boolean, default=False)
    ticket_id = Column(String(50), nullable=True)
    knowledge_articles = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KnowledgeSync(Base):
    __tablename__ = "knowledge_sync"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)  # bookstack, zammad
    source_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), nullable=True)