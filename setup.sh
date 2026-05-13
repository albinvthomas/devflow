#!/bin/bash

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Please update it with your secrets."
fi

# Run docker-compose up
echo "Building and starting DevFlow..."
docker compose up --build -d

echo ""
echo "=================================================="
echo "DevFlow is running at http://localhost:5173"
echo "=================================================="
