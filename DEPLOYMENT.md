# Deployment Guide

This guide provides comprehensive instructions for deploying the AI-powered web research application in various environments, from development to production.

## 🐳 Docker Deployment (Recommended)

Docker deployment provides the most reliable and consistent deployment method across different environments.

### Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.0+
- Google Gemini API key
- At least 2GB RAM
- At least 5GB available disk space

### Quick Docker Deployment

#### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
LANGSMITH_API_KEY=your_langsmith_key_for_observability

# Search Provider API Keys (optional but recommended)
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_API_KEY=your_google_api_key
SEARCHAPI_KEY=your_searchapi_io_key
```

#### 2. Build and Deploy

```bash
# Build the Docker image
docker build -t gemini-fullstack-langgraph -f Dockerfile .

# Start the full stack with Docker Compose
GEMINI_API_KEY=your_api_key docker-compose up

# Or with environment file
docker-compose --env-file .env up
```

#### 3. Access Application

- **Frontend**: http://localhost:8123/app
- **Backend API**: http://localhost:8123/docs (Swagger UI)
- **Health Check**: http://localhost:8123/health

### Docker Compose Configuration

The `docker-compose.yml` includes:

```yaml
services:
  langgraph-redis:
    image: redis:6
    # Redis for caching and session management
    
  langgraph-postgres:  
    image: postgres:16
    # PostgreSQL for data persistence
    
  langgraph-api:
    image: gemini-fullstack-langgraph
    ports: ["8123:8000"]
    # Main application container
```

### Docker Build Process

The multi-stage Dockerfile optimizes for production:

#### Stage 1: Frontend Build
```dockerfile
FROM node:20-alpine AS frontend-builder
# Builds React frontend with Vite
# Outputs optimized static files
```

#### Stage 2: Backend Setup
```dockerfile
FROM docker.io/langchain/langgraph-api:3.11
# Installs Python dependencies with UV
# Copies frontend build
# Configures production environment
```

### Production Docker Deployment

#### Docker Swarm (Single-Node)

```bash
# Initialize Docker Swarm
docker swarm init

# Deploy as a stack
docker stack deploy -c docker-compose.yml research-app

# Check service status
docker service ls
```

#### Docker with Nginx Reverse Proxy

Create `nginx.conf`:

```nginx
upstream research_backend {
    server localhost:8123;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://research_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Deploy with Nginx:

```bash
# Start the application
docker-compose up -d

# Start Nginx (assumes Nginx is installed on host)
sudo nginx -s reload
```

## ☁️ Cloud Platform Deployments

### AWS Deployment

#### AWS ECS with Fargate

1. **Create ECR Repository**

```bash
# Create ECR repository
aws ecr create-repository --repository-name research-app

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t research-app .
docker tag research-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/research-app:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/research-app:latest
```

2. **ECS Task Definition**

```json
{
  "family": "research-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "research-app",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/research-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GEMINI_API_KEY",
          "value": "your-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/research-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name research-cluster

# Create service
aws ecs create-service \
  --cluster research-cluster \
  --service-name research-service \
  --task-definition research-app \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}'
```

#### AWS Lambda with API Gateway

For serverless deployment (suitable for low-traffic scenarios):

```python
# lambda_handler.py
import json
from mangum import Mangum
from agent.app import app

handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

Deploy with AWS SAM:

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ResearchFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Runtime: python3.11
      Timeout: 900  # 15 minutes for research tasks
      MemorySize: 2048
      Environment:
        Variables:
          GEMINI_API_KEY: !Ref GeminiApiKey
      Events:
        ResearchApi:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push to Container Registry
docker build -t gcr.io/your-project-id/research-app .
docker push gcr.io/your-project-id/research-app

# Deploy to Cloud Run
gcloud run deploy research-app \
  --image gcr.io/your-project-id/research-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-api-key \
  --memory 2Gi \
  --timeout 900
```

### Microsoft Azure

#### Azure Container Instances

```bash
# Create resource group
az group create --name research-rg --location eastus

# Deploy container
az container create \
  --resource-group research-rg \
  --name research-app \
  --image your-registry/research-app:latest \
  --dns-name-label research-app-unique \
  --ports 8000 \
  --environment-variables GEMINI_API_KEY=your-api-key \
  --cpu 2 \
  --memory 4
```

### DigitalOcean App Platform

Create `.do/app.yaml`:

```yaml
name: research-app
services:
- name: web
  source_dir: /
  github:
    repo: your-username/research-app
    branch: main
  run_command: uvicorn agent.app:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: GEMINI_API_KEY
    value: your-api-key
    type: SECRET
```

## 🖥️ Traditional Server Deployment

### Ubuntu/Debian Server Setup

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm git nginx

# Create application user
sudo useradd -m -s /bin/bash research-app
sudo usermod -aG sudo research-app
```

#### 2. Application Setup

```bash
# Switch to application user
sudo su - research-app

# Clone repository
git clone <repository-url> /home/research-app/app
cd /home/research-app/app

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# Frontend setup
cd ../frontend
npm install
npm run build

# Environment configuration
cd ..
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

#### 3. Systemd Service Configuration

Create `/etc/systemd/system/research-backend.service`:

```ini
[Unit]
Description=Research App Backend
After=network.target

[Service]
Type=simple
User=research-app
WorkingDirectory=/home/research-app/app/backend
Environment=PATH=/home/research-app/app/backend/venv/bin
ExecStart=/home/research-app/app/backend/venv/bin/uvicorn agent.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable research-backend
sudo systemctl start research-backend
sudo systemctl status research-backend
```

#### 4. Nginx Configuration

Create `/etc/nginx/sites-available/research-app`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve frontend static files
    location /app {
        alias /home/research-app/app/frontend/dist;
        try_files $uri $uri/ /app/index.html;
    }

    # Proxy API requests to backend
    location /api {
        rewrite ^/api/?(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct backend access
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/research-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 🔧 Environment Configuration

### Environment Variables Reference

#### Required Variables

```bash
# AI Model API Keys
GEMINI_API_KEY=your_gemini_api_key                 # Google Gemini (required)

# Optional AI Observability
LANGSMITH_API_KEY=your_langsmith_key               # LangSmith tracing (optional)
```

#### Optional Search Provider Variables

```bash
# Google Custom Search
GOOGLE_CSE_ID=your_custom_search_engine_id         # Google CSE ID
GOOGLE_API_KEY=your_google_api_key                 # Google API key

# Alternative Search Providers
SEARCHAPI_KEY=your_searchapi_io_key                # SearchAPI.io key
DUCKDUCKGO_API_KEY=your_duckduckgo_key            # DuckDuckGo API (if available)
```

#### Server Configuration Variables

```bash
# Backend Server
SERVER_HOST=0.0.0.0                               # Server bind address
SERVER_PORT=8000                                  # Server port
PYTHONPATH=/app/backend/src                       # Python path for imports

# Database Configuration (for Docker Compose)
POSTGRES_URI=postgres://user:pass@host:5432/db    # PostgreSQL connection
REDIS_URI=redis://host:6379                       # Redis connection

# Frontend Configuration (build-time)
VITE_API_URL=https://your-api-domain.com          # API endpoint override
```

### Configuration Management

#### Development Environment

```bash
# config.env - Development defaults
SERVER_HOST := 0.0.0.0
SERVER_PORT := 2024
FRONTEND_HOST := localhost
FRONTEND_PORT := 5173
VITE_API_TARGET := http://localhost:$(SERVER_PORT)
DEV_TIMEOUT := 120
```

#### Production Environment

```bash
# .env - Production configuration
GEMINI_API_KEY=prod_gemini_key
LANGSMITH_API_KEY=prod_langsmith_key
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
NODE_ENV=production
PYTHONPATH=/app/backend/src
```

#### Docker Environment Variables

```yaml
# docker-compose.yml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
  - POSTGRES_URI=postgres://postgres:postgres@langgraph-postgres:5432/postgres
  - REDIS_URI=redis://langgraph-redis:6379
```

## 📊 Monitoring and Logging

### Application Monitoring

#### Health Checks

The application provides built-in health monitoring:

```bash
# Basic health check
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "service": "atomic-research-agent"
}
```

#### Performance Monitoring

Enable performance profiling:

```python
# In production configuration
ENABLE_PERFORMANCE_PROFILING=true
PERFORMANCE_LOG_LEVEL=INFO
```

#### Log Configuration

Configure logging levels:

```bash
# Environment variables
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                   # json, text
LOG_FILE=/var/log/research-app.log
```

### External Monitoring Integration

#### Prometheus Metrics

Add metrics endpoint:

```python
# Optional: Add to agent/app.py
from prometheus_client import Counter, Histogram, generate_latest

research_requests = Counter('research_requests_total', 'Total research requests')
research_duration = Histogram('research_duration_seconds', 'Research duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Log Aggregation

Configure log shipping to external systems:

```bash
# For ELK Stack
filebeat -e -c filebeat.yml

# For Datadog
DD_API_KEY=your-key DD_SITE=datadoghq.com datadog-agent
```

## 🔧 Performance Optimization

### Production Optimizations

#### Backend Optimizations

```python
# agent/app.py - Production settings
from fastapi import FastAPI

app = FastAPI(
    title="Research API",
    docs_url="/docs" if os.getenv("NODE_ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("NODE_ENV") != "production" else None,
)

# Enable ASGI middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### Database Connection Pooling

```bash
# Environment variables for connection pooling
POSTGRES_MAX_CONNECTIONS=20
POSTGRES_MIN_CONNECTIONS=5
REDIS_CONNECTION_POOL_SIZE=10
```

#### Resource Limits

```yaml
# Docker Compose resource limits
services:
  langgraph-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Caching Strategies

#### Redis Caching

Configure Redis for response caching:

```python
# Add to configuration
REDIS_CACHE_TTL=3600              # 1 hour cache
REDIS_MAX_MEMORY=1G               # Memory limit
REDIS_EVICTION_POLICY=allkeys-lru # LRU eviction
```

#### Application-Level Caching

```python
# Enable request-scoped caching
ENABLE_REQUEST_CACHING=true
CACHE_SEARCH_RESULTS=true
CACHE_AI_RESPONSES=true
```

## 🚨 Troubleshooting

### Common Deployment Issues

#### 1. Container Won't Start

```bash
# Check container logs
docker logs langgraph-api

# Common causes:
# - Missing GEMINI_API_KEY
# - Port conflicts
# - Insufficient memory
# - Database connection issues
```

#### 2. API Key Issues

```bash
# Verify API key is set
docker exec langgraph-api env | grep GEMINI_API_KEY

# Test API key validity
curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models
```

#### 3. Memory Issues

```bash
# Check memory usage
docker stats langgraph-api

# Increase memory limits
docker-compose up --scale langgraph-api=1 -d
```

#### 4. Network Issues

```bash
# Check port binding
netstat -tlnp | grep 8123

# Test internal connectivity
docker exec langgraph-api curl -f http://localhost:8000/health
```

### Database Issues

#### PostgreSQL Connection Problems

```bash
# Check PostgreSQL logs
docker logs langgraph-postgres

# Test connection
docker exec langgraph-postgres pg_isready -U postgres

# Manual connection test
docker exec -it langgraph-postgres psql -U postgres
```

#### Redis Connection Issues

```bash
# Check Redis logs
docker logs langgraph-redis

# Test Redis connectivity
docker exec langgraph-redis redis-cli ping
```

### Performance Issues

#### Slow Response Times

1. Check external API latency
2. Monitor database query performance
3. Verify adequate CPU/memory resources
4. Review search provider rate limits

#### Memory Leaks

```bash
# Monitor memory usage over time
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check for memory leaks in logs
grep -i "memory\|oom" /var/log/research-app.log
```

## 🔄 Updates and Maintenance

### Application Updates

#### Docker Deployment Updates

```bash
# Pull latest image
docker pull your-registry/research-app:latest

# Rolling update with zero downtime
docker-compose up -d --no-deps langgraph-api

# Verify deployment
curl http://localhost:8123/health
```

#### Traditional Server Updates

```bash
# Update code
cd /home/research-app/app
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -e . --upgrade

# Rebuild frontend
cd ../frontend
npm install
npm run build

# Restart service
sudo systemctl restart research-backend
```

### Database Maintenance

#### PostgreSQL Maintenance

```bash
# Backup database
docker exec langgraph-postgres pg_dump -U postgres postgres > backup.sql

# Vacuum and analyze
docker exec langgraph-postgres psql -U postgres -c "VACUUM ANALYZE;"
```

#### Redis Maintenance

```bash
# Save Redis snapshot
docker exec langgraph-redis redis-cli BGSAVE

# Clear cache if needed
docker exec langgraph-redis redis-cli FLUSHALL
```

### Security Updates

#### Regular Security Tasks

1. **Update base images monthly**
2. **Rotate API keys quarterly**
3. **Review access logs weekly**
4. **Update SSL certificates automatically**
5. **Monitor security advisories**

---

This deployment guide covers various deployment scenarios from development to large-scale production environments. Choose the deployment method that best fits your infrastructure requirements and scaling needs.