import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class BookStackIntegration:
    def __init__(self):
        self.base_url = os.getenv("BOOKSTACK_URL", "http://bookstack:80")
        self.api_token = os.getenv("BOOKSTACK_API_TOKEN", "demo_token")
        self.api_secret = os.getenv("BOOKSTACK_API_SECRET", "demo_secret")
        self.session = None
        
    async def initialize(self):
        """Initialize BookStack integration"""
        try:
            logger.info("Initializing BookStack integration...")
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Token {self.api_token}:{self.api_secret}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self._test_connection()
            logger.info("BookStack integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BookStack integration: {str(e)}")
            # Don't raise exception to allow system to start

    async def _test_connection(self):
        """Test BookStack API connection"""
        try:
            if self.session is None:
                return
                
            async with self.session.get(f"{self.base_url}/api/books") as response:
                if response.status == 200:
                    logger.info("BookStack API connection successful")
                else:
                    logger.warning(f"BookStack API test failed with status: {response.status}")
        except Exception as e:
            logger.warning(f"BookStack API test failed: {str(e)}")

    async def search_articles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for articles in BookStack"""
        try:
            if self.session is None:
                logger.warning("BookStack session not initialized, returning mock results")
                return [
                    {
                        "id": 1,
                        "name": "Password Reset Guide",
                        "slug": "password-reset-guide",
                        "text": "Complete guide for resetting passwords...",
                        "url": f"{self.base_url}/books/guides/page/password-reset-guide",
                        "relevance": 0.95
                    },
                    {
                        "id": 2,
                        "name": "VPN Setup Instructions", 
                        "slug": "vpn-setup-instructions",
                        "text": "Step-by-step VPN configuration...",
                        "url": f"{self.base_url}/books/guides/page/vpn-setup-instructions",
                        "relevance": 0.87
                    }
                ]
            
            # BookStack search API
            params = {
                "query": query,
                "count": limit,
                "type": "page"
            }
            
            async with self.session.get(
                f"{self.base_url}/api/search",
                params=params
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    articles = []
                    
                    for item in results.get("data", []):
                        if item.get("type") == "page":
                            articles.append({
                                "id": item.get("id"),
                                "name": item.get("name"),
                                "slug": item.get("slug"),
                                "text": item.get("preview_text", ""),
                                "url": item.get("url"),
                                "relevance": item.get("relevance", 0.5)
                            })
                    
                    logger.info(f"Found {len(articles)} articles for query: {query}")
                    return articles
                else:
                    logger.error(f"BookStack search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching BookStack: {str(e)}")
            return []

    async def get_all_articles(self) -> List[Dict[str, Any]]:
        """Get all articles from BookStack for syncing"""
        try:
            if self.session is None:
                logger.warning("BookStack session not initialized, returning empty list")
                return []
            
            articles = []
            page = 1
            per_page = 50
            
            while True:
                params = {
                    "count": per_page,
                    "offset": (page - 1) * per_page
                }
                
                async with self.session.get(
                    f"{self.base_url}/api/pages",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get("data", [])
                        
                        if not pages:
                            break
                            
                        for page_data in pages:
                            # Get full page content
                            page_detail = await self._get_page_detail(page_data["id"])
                            if page_detail:
                                articles.append(page_detail)
                        
                        page += 1
                        if len(pages) < per_page:
                            break
                    else:
                        logger.error(f"Failed to get BookStack pages: {response.status}")
                        break
            
            logger.info(f"Retrieved {len(articles)} articles from BookStack")
            return articles
            
        except Exception as e:
            logger.error(f"Error getting all BookStack articles: {str(e)}")
            return []

    async def _get_page_detail(self, page_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed page content"""
        try:
            async with self.session.get(f"{self.base_url}/api/pages/{page_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Failed to get page {page_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting page detail {page_id}: {str(e)}")
            return None

    async def get_statistics(self) -> Dict[str, Any]:
        """Get BookStack statistics"""
        try:
            if self.session is None:
                return {
                    "total_pages": 0,
                    "total_books": 0,
                    "total_chapters": 0
                }
            
            stats = {}
            
            # Get books count
            async with self.session.get(f"{self.base_url}/api/books?count=1") as response:
                if response.status == 200:
                    data = await response.json()
                    stats["total_books"] = data.get("total", 0)
            
            # Get pages count  
            async with self.session.get(f"{self.base_url}/api/pages?count=1") as response:
                if response.status == 200:
                    data = await response.json()
                    stats["total_pages"] = data.get("total", 0)
            
            # Get chapters count
            async with self.session.get(f"{self.base_url}/api/chapters?count=1") as response:
                if response.status == 200:
                    data = await response.json()
                    stats["total_chapters"] = data.get("total", 0)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting BookStack statistics: {str(e)}")
            return {}

    async def close(self):
        """Close BookStack integration"""
        if self.session:
            await self.session.close()