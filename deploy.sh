#!/bin/bash

set -e

echo "AutoTrading Bot EC2 Deployment Script"
echo "======================================"

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with your API keys."
    echo "Copy .env.example to .env and fill in your values."
    exit 1
fi

echo "Building Docker image..."
docker build -t autotrading-bot .

echo "Stopping existing container if running..."
docker-compose down || true

echo "Starting container with docker-compose..."
docker-compose up -d

echo "Checking container status..."
docker-compose ps

echo "Showing container logs (last 20 lines)..."
docker-compose logs --tail=20 autotrading

echo ""
echo "Deployment complete!"
echo "Monitor logs with: docker-compose logs -f autotrading"
echo "Stop with: docker-compose down"