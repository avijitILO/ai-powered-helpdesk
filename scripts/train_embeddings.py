#!/usr/bin/env python3
"""
Train embeddings and populate vector database with initial knowledge base
"""

import sys
import os
import json
import asyncio
import logging
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import RAGService
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmbeddingTrainer:
    def __init__(self):
        self.rag_service = RAGService()
        self.knowledge_base_path = "/app/data/knowledge_base.json"
        self.demo_tickets_path = "/app/data/demo_tickets.json"
        self.department_rules_path = "/app/data/department_rules.json"
        
    async def initialize(self):
        """Initialize services"""
        logger.info("Initializing RAG service...")
        await self.rag_service.initialize()
        logger.info("RAG service initialized successfully")
        
    async def load_knowledge_base(self):
        """Load and index knowledge base articles"""
        if not os.path.exists(self.knowledge_base_path):
            logger.warning(f"Knowledge base file not found: {self.knowledge_base_path}")
            logger.info("Creating default knowledge base...")
            await self.create_default_knowledge_base()
            return
            
        with open(self.knowledge_base_path, 'r') as f:
            data = json.load(f)
            
        articles = data.get('articles', [])
        logger.info(f"Loading {len(articles)} knowledge base articles...")
        
        for i, article in enumerate(articles):
            try:
                doc_id = await self.rag_service.add_document({
                    "title": article['title'],
                    "content": article['content'],
                    "department": article.get('department', 'General'),
                    "category": article.get('category', 'General'),
                    "metadata": {
                        "source": "knowledge_base",
                        "type": "article",
                        "tags": article.get('tags', [])
                    }
                })
                logger.info(f"✓ Added article {i+1}/{len(articles)}: {article['title']}")
            except Exception as e:
                logger.error(f"✗ Failed to add article '{article['title']}': {str(e)}")
                
    async def create_default_knowledge_base(self):
        """Create default knowledge base if files don't exist"""
        default_articles = [
            {
                "title": "Password Reset Process",
                "content": """To reset your password:
1. Go to the login page
2. Click on 'Forgot Password'
3. Enter your email address
4. Check your email for the reset link
5. Click the link and create a new password
6. Password must be at least 8 characters with one uppercase, one number, and one special character

If you don't receive the email within 5 minutes, check your spam folder or contact IT support.""",
                "department": "IT",
                "category": "Authentication",
                "tags": ["password", "reset", "login", "authentication"]
            },
            {
                "title": "VPN Connection Guide",
                "content": """To connect to company VPN:
1. Download the VPN client from the IT portal
2. Install the client with administrator privileges
3. Launch the VPN client
4. Server address: vpn.company.com
5. Enter your domain credentials (same as computer login)
6. Click Connect

Troubleshooting:
- If connection fails, ensure you're connected to internet
- Check if your VPN certificate is valid (expires every 90 days)
- For certificate renewal, contact IT support""",
                "department": "IT",
                "category": "Network",
                "tags": ["vpn", "remote", "connection", "network"]
            },
            {
                "title": "Leave Application Process",
                "content": """To apply for leave:
1. Log into the HR portal at hr.company.com
2. Navigate to 'Leave Management'
3. Click 'Apply for Leave'
4. Select leave type (Annual/Sick/Personal)
5. Choose start and end dates
6. Add reason/comments
7. Attach supporting documents if required
8. Submit for approval

Leave balance and history can be viewed in the same portal.
Approval typically takes 1-2 business days.""",
                "department": "HR",
                "category": "Leave",
                "tags": ["leave", "vacation", "time off", "absence"]
            }
        ]
        
        # Create data directory if it doesn't exist
        os.makedirs("/app/data", exist_ok=True)
        
        # Save default knowledge base
        with open(self.knowledge_base_path, 'w') as f:
            json.dump({"articles": default_articles}, f, indent=2)
            
        logger.info(f"Created default knowledge base with {len(default_articles)} articles")
        
        # Index the articles
        for i, article in enumerate(default_articles):
            try:
                doc_id = await self.rag_service.add_document({
                    "title": article['title'],
                    "content": article['content'],
                    "department": article['department'],
                    "category": article['category'],
                    "metadata": {
                        "source": "default",
                        "type": "article",
                        "tags": article.get('tags', [])
                    }
                })
                logger.info(f"✓ Added default article {i+1}/{len(default_articles)}: {article['title']}")
            except Exception as e:
                logger.error(f"✗ Failed to add article '{article['title']}': {str(e)}")
                
    async def cleanup(self):
        """Cleanup resources"""
        await self.rag_service.cleanup()


async def main():
    """Main training function"""
    trainer = EmbeddingTrainer()
    
    try:
        await trainer.initialize()
        await trainer.load_knowledge_base()
        logger.info("\n✅ Embedding training completed successfully!")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise
    finally:
        await trainer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())