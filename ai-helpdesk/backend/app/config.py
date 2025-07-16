from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://helpdesk:helpdesk123@postgres:5432/helpdesk_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "helpdesk_docs"
    
    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Zammad
    ZAMMAD_URL: str = "http://zammad-nginx:8080"
    ZAMMAD_TOKEN: Optional[str] = None
    
    # BookStack
    BOOKSTACK_URL: str = "http://bookstack:80"
    BOOKSTACK_TOKEN_ID: Optional[str] = None
    BOOKSTACK_TOKEN_SECRET: Optional[str] = None
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

settings = Settings()