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
docker exec helpdesk-backend cd app
docker exec helpdesk-backend mkdir scripts
cp script/init_db.py /app/scripts/init_db.py
docker exec helpdesk-backend python scripts/init_db.py

# Load demo data
echo "Loading demo data..."
cp script/load_demo_data.py /app/scripts/load_demo_data.py
docker exec helpdesk-backend python scripts/load_demo_data.py

# Train initial embeddings
echo "Training initial embeddings..."
cp script/train_embeddings.py /app/scripts/train_embeddings.py
docker exec helpdesk-backend python scripts/train_embeddings.py

#check container are running
echo "check container are running"
docker ps | grep helpdesk

#healthcheck
echo ""
echo "🧪 Testing services..."
echo -n "Backend API: "
if curl -s http://localhost:8000 | grep -q "AI Helpdesk"; then
    echo "✅ Working"
else
    echo "❌ Not responding"
fi

echo -n "Ollama API: "
if curl -s http://localhost:11434 | grep -q "Ollama"; then
    echo "✅ Working"
else
    echo "❌ Not responding"
fi

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
