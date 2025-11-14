#!/bin/bash

# AI Hotel Assistant - Local Startup Script

echo "🚀 Starting AI Hotel Assistant..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not available."
    exit 1
fi

# Check for .env files
if [ ! -f backend/.env ]; then
    echo "⚠️  Backend .env file not found. Creating from example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your API keys"
    echo "   Required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
    read -p "Press Enter after configuring your API keys..."
fi

if [ ! -f frontend/.env ]; then
    echo "⚠️  Frontend .env file not found. Creating from example..."
    cp frontend/.env.example frontend/.env
fi

echo "📦 Starting services with Docker Compose..."
echo ""

# Use docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null 2>&1; then
    docker compose up --build
else
    docker-compose up --build
fi