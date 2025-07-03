#!/bin/bash

if ! command -v docker &> /dev/null; then
    echo "Docker not found, installing..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
fi

sudo docker stop pyvrp_runner 2>/dev/null || true
sudo docker rm pyvrp_runner 2>/dev/null || true

echo "Pruning unused Docker resources..."
sudo docker system prune -af

echo "Loading Docker image..."
sudo docker load < pyvrp_docker_uploadable.tar

echo "Starting container..."
sudo docker run -dit -p 80:80 --name pyvrp_runner pyvrp_docker_uploadable
