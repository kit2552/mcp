#!/bin/bash

# AI Hotel Assistant - Setup Validation Script

echo "🔍 Validating AI Hotel Assistant Setup..."
echo ""

ERRORS=0

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env file not found"
    echo "   Run: cp backend/.env.example backend/.env"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ backend/.env file exists"
    
    # Check if API key is configured
    if grep -q "your-openai-api-key-here" backend/.env; then
        echo "❌ OpenAI API key not configured in backend/.env"
        echo "   Please add a valid API key from: https://platform.openai.com/api-keys"
        ERRORS=$((ERRORS + 1))
    elif grep -q "your-anthropic-api-key-here" backend/.env && grep -q 'LLM_PROVIDER="anthropic"' backend/.env; then
        echo "❌ Anthropic API key not configured in backend/.env"
        echo "   Please add a valid API key from: https://console.anthropic.com/settings/keys"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ API key is configured"
    fi
    
    # Check MongoDB configuration
    if grep -q '^MONGO_URL=' backend/.env | grep -v '^#'; then
        echo "⚠️  MongoDB is enabled in backend/.env"
        echo "   For testing without database, use: docker-compose -f docker-compose.simple.yml up"
    else
        echo "✅ MongoDB is disabled (good for testing)"
    fi
fi

# Check if frontend .env exists
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  frontend/.env file not found (will use defaults)"
    echo "   Optional: cp frontend/.env.example frontend/.env"
else
    echo "✅ frontend/.env file exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo "✅ Setup validation passed!"
    echo ""
    echo "Ready to start:"
    echo "  • Without database: docker-compose -f docker-compose.simple.yml up"
    echo "  • With database:    docker-compose up"
    exit 0
else
    echo "❌ Found $ERRORS error(s). Please fix them before starting."
    exit 1
fi
