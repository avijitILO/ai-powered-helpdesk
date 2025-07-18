from fastapi import APIRouter, Query
from typing import List, Dict, Any

router = APIRouter()

@router.get("/articles/search")
async def search_articles(q: str = Query(..., description="Search query")):
    """Search knowledge base"""
    return []

@router.post("/articles")
async def create_article(article: Dict[str, Any]):
    """Create article"""
    return {"id": "article-123", "message": "Article created"}