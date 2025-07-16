AI Helpdesk Application 
Technology Stack

Backend: FastAPI (Python 3.11)
AI/ML: Langchain + Ollama + HuggingFace Embeddings
Vector Database: Qdrant
Database: PostgreSQL
Cache: Redis
Ticketing System: Zammad (Open Source)
Knowledge Base: BookStack (Open Source)
Frontend: React
Containerization: Docker & Docker Compose

ai-helpdesk/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── tickets.py
│   │   │   └── knowledge.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── ticket_service.py
│   │   │   └── knowledge_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py
│   │   │   └── knowledge.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── embeddings.py
│   │       └── department_classifier.py
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/
│   ├── demo_tickets.json
│   ├── knowledge_base.json
│   └── department_rules.json
├── scripts/
│   ├── init_db.py
│   ├── load_demo_data.py
│   └── train_embeddings.py
└── config/
    ├── nginx.conf
    └── zammad_config.rb