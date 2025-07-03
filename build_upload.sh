#!/bin/bash

set -e

read -p "Enter the instance name: " instance_name
read -p "Enter the zone: " zone

IMAGE_NAME="pyvrp_docker_uploadable"
TAR_NAME="$IMAGE_NAME.tar"

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Saving image to $TAR_NAME..."
docker save $IMAGE_NAME -o $TAR_NAME

echo "Copying image and startup script to VM..."
gcloud compute scp $TAR_NAME start_container.sh "$instance_name:~" --zone="$zone"

echo "Running startup script on VM..."
gcloud compute ssh "$instance_name" --zone="$zone" --command="bash start_container.sh"