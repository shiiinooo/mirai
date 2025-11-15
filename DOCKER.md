# Docker Deployment Guide

This guide explains how to deploy mirai using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Set up environment variables:**

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# SerpAPI Configuration
SERPAPI_API_KEY=your_serpapi_key_here

# Frontend API URL (use backend service name in docker-compose)
VITE_API_URL=http://backend:8000
```

2. **Build and start services:**

```bash
docker-compose up -d --build
```

3. **Access the application:**

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Mode

The default `docker-compose.yml` includes volume mounts for hot-reloading:

```bash
docker-compose up
```

Changes to code will be reflected without rebuilding (backend only).

## Production Mode

Use `docker-compose.prod.yml` for production (no volume mounts):

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Useful Commands

**View logs:**
```bash
docker-compose logs -f
```

**View backend logs only:**
```bash
docker-compose logs -f backend
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove volumes:**
```bash
docker-compose down -v
```

**Rebuild services:**
```bash
docker-compose up -d --build
```

**Check service status:**
```bash
docker-compose ps
```

**Execute commands in containers:**
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

## Environment Variables

### Backend (ai-service)

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_MODEL` (optional): Model to use (default: gpt-4o-mini)
- `SERPAPI_API_KEY` (required): Your SerpAPI key for flight/hotel data

### Frontend (platform)

- `VITE_API_URL` (optional): Backend API URL (default: http://backend:8000)

**Note:** For the frontend, `VITE_API_URL` must be set at build time. If you need to change it, rebuild the frontend image.

## Networking

Both services are on the same Docker network (`mirai-network`), so they can communicate using service names:
- Backend is accessible at `http://backend:8000` from the frontend container
- Frontend is accessible at `http://frontend:80` from the backend container

## Health Checks

The backend includes a health check that runs every 30 seconds. The frontend waits for the backend to be healthy before starting.

## Troubleshooting

**Backend won't start:**
- Check that environment variables are set correctly
- Verify API keys are valid
- Check logs: `docker-compose logs backend`

**Frontend can't connect to backend:**
- Ensure `VITE_API_URL` is set to `http://backend:8000` (not `localhost`)
- Rebuild the frontend: `docker-compose build frontend`
- Check network connectivity: `docker-compose exec frontend ping backend`

**Port already in use:**
- Change ports in `docker-compose.yml`:
  ```yaml
  ports:
    - "8001:8000"  # Backend on 8001
    - "8080:80"    # Frontend on 8080
  ```

## Building Individual Services

**Backend only:**
```bash
docker-compose build backend
```

**Frontend only:**
```bash
docker-compose build frontend
```

## Production Considerations

1. **Use production compose file:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Set up reverse proxy** (nginx/traefik) for SSL/TLS

3. **Use secrets management** for API keys (Docker secrets, AWS Secrets Manager, etc.)

4. **Set resource limits** in production:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 2G
   ```

5. **Enable logging** to external service (ELK, CloudWatch, etc.)

6. **Use health checks** for orchestration (Kubernetes, Docker Swarm)

