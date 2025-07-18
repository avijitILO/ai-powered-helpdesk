#!/bin/bash

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

# 11. Show final status
echo ""
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep helpdesk || echo "No helpdesk containers found"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🌐 Access your application:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "📝 If you encounter issues:"
echo "   1. Check logs: docker-compose logs [service-name]"
echo "   2. Restart: docker-compose restart"
echo "   3. Full reset: docker-compose down -v && docker-compose up -d"
echo ""
echo "💡 The setup is now complete and should be working!"