@echo off
REM AI Hotel Assistant - Local Startup Script for Windows

echo Starting AI Hotel Assistant...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check for .env files
if not exist backend\.env (
    echo Backend .env file not found. Creating from example...
    copy backend\.env.example backend\.env
    echo Please edit backend\.env and add your API keys
    echo Required: OPENAI_API_KEY or ANTHROPIC_API_KEY
    pause
)

if not exist frontend\.env (
    echo Frontend .env file not found. Creating from example...
    copy frontend\.env.example frontend\.env
)

echo Starting services with Docker Compose...
echo.

REM Try docker compose v2 first, then fall back to docker-compose v1
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose up --build
) else (
    docker compose up --build
)