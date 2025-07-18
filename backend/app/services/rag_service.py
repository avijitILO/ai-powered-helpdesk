from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import uuid
from ..config import settings

class RAGService:
    def __init__(self):
        self.client = None
        self.embedder = None
        self.collection_name = settings.QDRANT_COLLECTION
        
    async def initialize(self):
        """Initialize RAG service with Qdrant and embeddings"""
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Create collection if not exists
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 dimension
                    distance=Distance.COSINE
                )
            )
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        return self.embedder.encode(text).tolist()
    
    async def add_document(self, document: Dict[str, Any]) -> str:
        """Add document to vector store"""
        doc_id = str(uuid.uuid4())
        embedding = self.create_embedding(document["content"])
        
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload={
                "title": document.get("title", ""),
                "content": document["content"],
                "category": document.get("category", "general"),
                "department": document.get("department", "IT"),
                "metadata": document.get("metadata", {})
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return doc_id
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        query_embedding = self.create_embedding(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "content": result.payload["content"],
                "title": result.payload.get("title", ""),
                "category": result.payload.get("category", ""),
                "department": result.payload.get("department", "")
            }
            for result in results
        ]
    
    async def get_context(self, query: str) -> str:
        """Get relevant context for query"""
        results = await self.search_documents(query, limit=3)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        context = "Relevant information from knowledge base:\\n\\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\\n{result['content']}\\n\\n"
        
        return context
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            self.client.close()