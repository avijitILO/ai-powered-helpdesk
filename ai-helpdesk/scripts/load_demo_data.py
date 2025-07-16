import sys
import os
import json
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import RAGService
from app.services.ticket_service import TicketService

async def load_demo_data():
    """Load demo data into the system"""
    rag_service = RAGService()
    ticket_service = TicketService()
    
    await rag_service.initialize()
    
    # Load knowledge base articles
    with open('/app/data/knowledge_base.json', 'r') as f:
        kb_data = json.load(f)
    
    print("Loading knowledge base articles...")
    for article in kb_data['articles']:
        doc_id = await rag_service.add_document({
            "title": article['title'],
            "content": article['content'],
            "department": article['department'],
            "category": article['category']
        })
        print(f"Added article: {article['title']} (ID: {doc_id})")
    
    # Load demo tickets
    with open('/app/data/demo_tickets.json', 'r') as f:
        ticket_data = json.load(f)
    
    print("\\nLoading demo tickets...")
    for ticket in ticket_data['tickets']:
        # Create resolved tickets for training
        ticket_id = await ticket_service.create_ticket({
            "title": ticket['title'],
            "description": ticket['description'],
            "department": ticket['department'],
            "user_id": "demo_user",
            "priority": ticket['priority'],
            "status": "resolved"
        })
        
        # Add resolution to knowledge base
        if ticket.get('resolution'):
            await rag_service.add_document({
                "title": f"Resolution: {ticket['title']}",
                "content": f"Problem: {ticket['description']}\\n\\nSolution: {ticket['resolution']}",
                "department": ticket['department'],
                "category": ticket['category']
            })
        
        print(f"Added ticket: {ticket['title']}")
    
    print("\\nDemo data loaded successfully!")

if __name__ == "__main__":
    asyncio.run(load_demo_data())