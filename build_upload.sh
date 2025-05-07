#!/bin/bash

read -p "Enter the instance name:  " instance_name 
read -p "Enter the zone: " zone

# Build and save Docker image
echo "Saving Docker image..."
docker build -t pyvrp_docker_uploadable .
docker save pyvrp_docker_uploadable > pyvrp_docker_uploadable.tar

# Copy Docker image and startup script to the VM
echo "Copying image and startup script to VM..."
gcloud compute scp pyvrp_docker_uploadable.tar start_container.sh $instance_name:~ --zone="$zone"

# Run the startup script remotely
echo "Running startup script on VM..."
gcloud compute ssh "$instance_name" --zone="$zone" --command="bash start_container.sh"
