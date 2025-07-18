import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import settings
from .rag_service import RAGService

class KnowledgeService:
    def __init__(self):
        self.bookstack_url = "http://bookstack:80/api"
        self.bookstack_id = settings.BOOKSTACK_TOKEN_ID if hasattr(settings, 'BOOKSTACK_TOKEN_ID') else None
        self.bookstack_secret = settings.BOOKSTACK_TOKEN_SECRET if hasattr(settings, 'BOOKSTACK_TOKEN_SECRET') else None
        self.rag_service = RAGService()
        
    async def create_article(self, article_data: Dict[str, Any]) -> str:
        """Create article in both BookStack and vector DB"""
        # First add to vector database
        doc_id = await self.rag_service.add_document({
            "title": article_data["title"],
            "content": article_data["content"],
            "department": article_data.get("department", "General"),
            "category": article_data.get("category", "General"),
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "source": "user_query"
            }
        })
        
        # Then create in BookStack if configured
        if self.bookstack_id and self.bookstack_secret:
            await self._create_bookstack_page(article_data)
            
        return doc_id
    
    async def _create_bookstack_page(self, article_data: Dict[str, Any]):
        """Create page in BookStack"""
        headers = {
            "Authorization": f"Token {self.bookstack_id}:{self.bookstack_secret}",
            "Content-Type": "application/json"
        }
        
        # First, get or create a book
        book_id = await self._get_or_create_book(article_data.get("department", "General"))
        
        page_data = {
            "book_id": book_id,
            "name": article_data["title"],
            "html": f"<h1>{article_data['title']}</h1><p>{article_data['content']}</p>"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.bookstack_url}/pages",
                    headers=headers,
                    json=page_data,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Error creating BookStack page: {e}")
                
    async def _get_or_create_book(self, name: str) -> int:
        """Get or create a BookStack book"""
        headers = {
            "Authorization": f"Token {self.bookstack_id}:{self.bookstack_secret}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Try to get existing books
                response = await client.get(
                    f"{self.bookstack_url}/books",
                    headers=headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    books = response.json().get("data", [])
                    for book in books:
                        if book.get("name") == name:
                            return book["id"]
                
                # Create new book if not found
                book_data = {"name": name, "description": f"{name} Knowledge Base"}
                response = await client.post(
                    f"{self.bookstack_url}/books",
                    headers=headers,
                    json=book_data,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()["id"]
                    
            except Exception as e:
                print(f"Error with BookStack book: {e}")
                
        return 1  # Default book ID
    
    async def search_bookstack(self, query: str) -> List[Dict[str, Any]]:
        """Search BookStack for articles"""
        if not self.bookstack_id:
            return []
            
        headers = {
            "Authorization": f"Token {self.bookstack_id}:{self.bookstack_secret}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.bookstack_url}/search",
                    params={"query": query, "type": "page"},
                    headers=headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json().get("data", [])
            except Exception as e:
                print(f"Error searching BookStack: {e}")
                
        return []