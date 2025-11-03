#!/bin/bash

# Petrol Station Management System - Docker Deployment Script
# This script helps deploy the application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
OVERRIDE_FILE="docker-compose.override.yml"
PROJECT_NAME="petrol-station"

echo -e "${BLUE}🐳 Starting Petrol Station Management System Docker Deployment${NC}"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [[ -f ".env.production" ]]; then
        cp .env.production .env
        echo -e "${RED}⚠️  IMPORTANT: Please edit .env file with your production settings!${NC}"
    else
        echo -e "${RED}❌ .env.production template not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs backups ssl nginx-logs mysql-init

# Function to use docker compose (v2) or docker-compose (v1)
docker_compose_cmd() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# Stop and remove existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker_compose_cmd -f $COMPOSE_FILE down --volumes --remove-orphans 2>/dev/null || true

# Build and start services
echo -e "${YELLOW}🏗️  Building and starting services...${NC}"

# For production deployment, use only the main compose file
if [[ "$1" == "dev" ]]; then
    echo -e "${BLUE}🚀 Starting in development mode...${NC}"
    docker_compose_cmd -f $COMPOSE_FILE -f $OVERRIDE_FILE up --build -d
else
    echo -e "${BLUE}🚀 Starting in production mode...${NC}"
    docker_compose_cmd -f $COMPOSE_FILE up --build -d
fi

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

# Check service status
echo -e "${YELLOW}📊 Checking service status...${NC}"
docker_compose_cmd ps

# Test database connection
echo -e "${YELLOW}🗄️  Testing database connection...${NC}"
if docker_compose_cmd exec -T petrol-station-db mysqladmin ping -h localhost --silent; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
fi

# Test application health
echo -e "${YELLOW}🏥 Testing application health...${NC}"
if curl -f http://localhost/health &>/dev/null; then
    echo -e "${GREEN}✅ Application health check passed${NC}"
else
    echo -e "${RED}⚠️  Application health check failed (may still be starting)${NC}"
fi

# Show logs
echo -e "${YELLOW}📝 Showing recent logs...${NC}"
docker_compose_cmd logs --tail=20

echo ""
echo -e "${GREEN}🎉 Docker deployment completed!${NC}"
echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo "  Web Application: http://localhost"
echo "  Database: localhost:3306"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Update:       docker-compose pull && docker-compose up -d"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  Services:     docker-compose ps"
echo "  Resources:    docker stats"
echo ""
echo -e "${YELLOW}⚠️  Next steps:${NC}"
echo "- Access the application at http://localhost"
echo "- Setup SSL certificate for production"
echo "- Configure domain name"
echo "- Update .env file with production credentials"
echo "- Test all application features"
