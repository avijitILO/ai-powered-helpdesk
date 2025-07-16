#!/bin/bash

echo "🔍 Checking AI Helpdesk System Health..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Check container status
echo "📊 Container Status:"
docker-compose ps

echo -e "\n🏥 Service Health Checks:"

# Check each service
services=(
    "postgres:5432:Database"
    "redis:6379:Redis"
    "localhost:11434:Ollama (AI)"
    "localhost:6333:Qdrant (Vector DB)"
    "localhost:8000:AI Service"
    "localhost:8080:Zammad"
    "localhost:6875:BookStack"
    "localhost:3000:Frontend"
    "localhost:8025:MailHog"
)

for service in "${services[@]}"; do
    IFS=':' read -r host port name <<< "$service"
    echo -n "$name: "
    
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        echo "✅ Running"
    else
        echo "❌ Not accessible"
    fi
done

echo -e "\n🎯 Quick Access URLs:"
echo "  Main Dashboard:    http://localhost:3000"
echo "  AI Service API:    http://localhost:8000/docs"
echo "  Zammad Tickets:    http://localhost:8080"
echo "  BookStack KB:      http://localhost:6875"
echo "  Email Testing:     http://localhost:8025"

echo -e "\n✅ Health check completed!"