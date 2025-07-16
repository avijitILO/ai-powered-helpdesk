import logging
from typing import List, Dict, Any, Optional
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import hashlib

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.collection_name = "helpdesk_knowledge"
        self.client = None
        self.embeddings_model = None
        
    async def initialize(self):
        """Initialize vector service"""
        try:
            logger.info("Initializing Vector Service...")
            
            # Initialize Qdrant client
            self.client = QdrantClient(url=self.qdrant_url)
            
            # Initialize embeddings model
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            logger.info("Vector Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector Service: {str(e)}")
            # Don't raise to allow system to start

    async def _ensure_collection_exists(self):
        """Ensure the collection exists in Qdrant"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")

    async def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the vector database"""
        try:
            if not self.client or not self.embeddings_model:
                logger.warning("Vector service not properly initialized")
                return False
            
            # Generate embedding
            embedding = self.embeddings_model.encode(content).tolist()
            
            # Generate unique ID based on content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            point_id = abs(hash(content_hash)) % (10**9)
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "content_hash": content_hash,
                    **metadata
                }
            )
            
            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added document to vector database: {metadata.get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector database: {str(e)}")
            return False

    async def similarity_search(self, query: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not self.client or not self.embeddings_model:
                logger.warning("Vector service not properly initialized")
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query).tolist()
            
            # Search for similar documents
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("content", ""),
                    "title": result.payload.get("title", ""),
                    "source": result.payload.get("source", ""),
                    "url": result.payload.get("url", ""),
                    "score": result.score,
                    "metadata": result.payload
                })
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            return []

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            if not self.client:
                return {}
            
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.distance,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}