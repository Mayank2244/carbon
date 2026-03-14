#!/bin/bash

# CarbonSense AI - All-in-one execution script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CarbonSense AI Backend...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --port 8000 --reload &
BACKEND_PID=$!

echo -e "${GREEN}Starting CarbonSense AI Frontend...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo -e "${BLUE}Backend PID: $BACKEND_PID${NC}"
echo -e "${GREEN}Frontend PID: $FRONTEND_PID${NC}"
echo -e "Application is starting..."
echo -e "Frontend: http://localhost:5173"
echo -e "Backend: http://localhost:8000"

# Function to kill child processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
