#!/bin/bash

echo "Setting up AI Helpdesk Application..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create .env file from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update with your API tokens."
fi

# Pull and start services
echo "Starting Docker services..."
docker-compose pull
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 30

# Initialize Ollama with llama2 model
echo "Downloading Ollama model..."
#docker exec ai-helpdesk-ollama-1 ollama pull llama2
docker exec helpdesk-ollama ollama pull llama3.1:8b-instruct-q4_0

# Initialize databases
echo "Initializing databases..."
docker exec ai-helpdesk-backend-1 python scripts/init_db.py

# Load demo data
echo "Loading demo data..."
docker exec helpdesk-backend python scripts/load_demo_data.py

# Train initial embeddings
echo "Training initial embeddings..."
docker exec helpdesk-backend python scripts/train_embeddings.py

echo "Setup complete!"
echo ""
echo "Access the applications at:"
echo "- Chat Interface: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Zammad (Tickets): http://localhost:8080"
echo "- BookStack (KB): http://localhost:6875"
echo ""
echo "Default credentials:"
echo "- Zammad: admin@example.com / admin123"
echo "- BookStack: admin@admin.com / password"
