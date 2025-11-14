# Deployment Guide

## Overview

This guide covers deploying the AI Hotel Assistant to various platforms.

## Local Development

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed local setup instructions.

## Docker Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: hotel_assistant_db
    volumes:
      - mongodb_prod_data:/data/db
    networks:
      - hotel-assistant-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017
      - DB_NAME=hotel_assistant_db
    env_file:
      - ./backend/.env.production
    depends_on:
      - mongodb
    networks:
      - hotel-assistant-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - hotel-assistant-network

volumes:
  mongodb_prod_data:

networks:
  hotel-assistant-network:
    driver: bridge
```

### Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run docker-compose

#### Using ECS (Elastic Container Service)

1. Build and push images to ECR
2. Create ECS task definitions
3. Set up ECS service
4. Configure load balancer
5. Set up MongoDB on DocumentDB or Atlas

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push backend
gcloud builds submit --tag gcr.io/PROJECT_ID/hotel-assistant-backend ./backend
gcloud run deploy backend --image gcr.io/PROJECT_ID/hotel-assistant-backend

# Build and push frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/hotel-assistant-frontend ./frontend
gcloud run deploy frontend --image gcr.io/PROJECT_ID/hotel-assistant-frontend
```

### Azure

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name hotel-assistant-rg --location eastus

# Deploy containers
az container create --resource-group hotel-assistant-rg \
  --name hotel-assistant --image your-registry/hotel-assistant
```

## Database Hosting

### MongoDB Atlas (Recommended)

1. Create account at mongodb.com/cloud/atlas
2. Create cluster
3. Get connection string
4. Update `MONGO_URL` in backend/.env

### Self-Hosted MongoDB

- Use Docker container
- Or install on VPS
- Enable authentication
- Configure backups

## Environment Variables

### Production Backend (.env.production)

```env
MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/hotel_assistant_db"
DB_NAME="hotel_assistant_db"
CORS_ORIGINS="https://yourdomain.com"

LLM_PROVIDER="openai"
OPENAI_API_KEY="${OPENAI_API_KEY}"

MCP_SEARCH_SERVER_TYPE="remote"
MCP_SEARCH_SERVER_URL="https://your-mcp-server.com"
```

### Production Frontend (.env.production)

```env
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api {
        proxy_pass http://backend:8001;
    }
}
```

## Monitoring

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/api/health

# Check all services
docker-compose ps
```

### Logging

Set up centralized logging:
- CloudWatch (AWS)
- Stackdriver (GCP)
- Application Insights (Azure)

## Backup Strategy

### MongoDB Backups

```bash
# Manual backup
mongodump --uri="mongodb://localhost:27017/hotel_assistant_db" --out=/backups/$(date +%Y%m%d)

# Automated daily backups
0 2 * * * /usr/bin/mongodump --uri="$MONGO_URL" --out=/backups/$(date +\%Y\%m\%d)
```

## Scaling

### Horizontal Scaling

- Deploy multiple backend instances
- Use load balancer
- Share MongoDB connection

### Vertical Scaling

- Increase container resources
- Upgrade server instance

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Enable MongoDB authentication
- [ ] Rotate API keys regularly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Use secrets management
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities
- [ ] Set up API authentication
- [ ] Configure CORS properly

## Rollback Procedure

```bash
# Stop current deployment
docker-compose down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and deploy
docker-compose up --build -d

# Verify deployment
curl http://localhost:8001/api/health
```

## CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build images
        run: docker-compose build
      
      - name: Push to registry
        run: |
          docker push your-registry/backend
          docker push your-registry/frontend
      
      - name: Deploy to server
        run: |
          ssh user@server 'cd app && docker-compose pull && docker-compose up -d'
```

---

For questions or issues, refer to the main [README.md](README.md).