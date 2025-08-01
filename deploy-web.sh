#!/bin/bash

set -e

echo "AutoTrading Web Dashboard Deployment Script"
echo "==========================================="

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with your API keys."
    exit 1
fi

echo "Building all services..."
docker-compose -f docker-compose.web.yml build

echo "Stopping existing containers..."
docker-compose -f docker-compose.web.yml down || true

echo "Starting all services..."
docker-compose -f docker-compose.web.yml up -d

echo "Checking container status..."
docker-compose -f docker-compose.web.yml ps

echo ""
echo "Deployment complete!"
echo "Dashboard available at: http://localhost:3000"
echo "API available at: http://localhost:8001"
echo ""
echo "Monitor logs with:"
echo "  Trading Bot: docker-compose -f docker-compose.web.yml logs -f autotrading-bot"
echo "  API Server:  docker-compose -f docker-compose.web.yml logs -f api-server"
echo "  Web App:     docker-compose -f docker-compose.web.yml logs -f web-dashboard"
echo ""
echo "Stop all services: docker-compose -f docker-compose.web.yml down"