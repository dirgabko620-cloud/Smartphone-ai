#!/bin/bash

# Quick start script for Smartphone AI

echo "🚀 Starting Smartphone AI..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Please run this script from the Smartphone AI root directory${NC}"
    exit 1
fi

# Function to run service in background
run_service() {
    local name=$1
    local command=$2
    
    echo -e "${YELLOW}Starting ${name}...${NC}"
    eval "$command" &
    echo -e "${GREEN}✅ ${name} started (PID: $!)${NC}"
}

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ Port $1 is already in use${NC}"
        return 1
    fi
    return 0
}

echo "🔍 Checking ports..."
check_port 8000 || exit 1
check_port 3000 || exit 1

# Start services
echo ""
echo -e "${GREEN}Starting services...${NC}"
echo ""

# Backend
run_service "Backend (FastAPI)" "cd backend && python main.py"
sleep 2

# Frontend
run_service "Frontend (React)" "cd frontend && npm start"
sleep 2

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Smartphone AI is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait