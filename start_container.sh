#!/bin/bash

# Install Docker if it's not installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found, installing..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Stop and remove old container if it exists
sudo docker stop pyvrp_runner 2>/dev/null || true
sudo docker rm pyvrp_runner 2>/dev/null || true

# Load the Docker image
echo "Loading Docker image..."
sudo docker load < pyvrp_docker_uploadable.tar

# Run container in detached mode
echo "Starting container..."
sudo docker run -dit -p 80:80 --name pyvrp_runner pyvrp_docker_uploadable

