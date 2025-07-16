#!/bin/bash

set -e

echo "🚀 Setting up Complete AI Helpdesk System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "📁 Creating required directories..."
mkdir -p logs/{ai-service,zammad,bookstack,nginx}
mkdir -p data/{postgres,redis,qdrant,ollama,elasticsearch,zammad,bookstack}

echo "🔧 Setting up permissions..."
chmod +x scripts/*.sh
chmod -R 755 data logs

echo "📋 Creating environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please review and update as needed."
fi

echo "🏗️ Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for services to initialize..."
sleep 60

echo "🤖 Downloading AI model..."
docker-compose exec -T ollama ollama pull llama2

echo "📊 Initializing demo data..."
./scripts/init_demo_data.sh

echo "🔍 Running health check..."
./scripts/health_check.sh

echo "✅ Setup complete!"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:     http://localhost:3000"
echo "  AI Service:   http://localhost:8000"
echo "  Zammad:       http://localhost:8080"
echo "  BookStack:    http://localhost:6875"
echo "  MailHog:      http://localhost:8025"
echo ""
echo "📚 Default Credentials:"
echo "  Zammad:    admin@example.com / test"
echo "  BookStack: admin@admin.com / password"
echo ""
echo "🎉 Your AI-powered helpdesk is ready!"