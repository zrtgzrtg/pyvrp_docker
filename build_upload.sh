#!/bin/bash

set -e  # Exit immediately on error

read -p "Enter the instance name:  " instance_name
read -p "Enter the zone: " zone

# Define image name
IMAGE_NAME="pyvrp_docker_uploadable"
TAR_NAME="$IMAGE_NAME.tar"

# 🐳 Build Docker image with no cache
echo "🚧 Building Docker image with --no-cache..."
docker build --no-cache --pull -t $IMAGE_NAME .

# 💾 Save Docker image as .tar file
echo "💾 Saving image to $TAR_NAME..."
docker save $IMAGE_NAME -o $TAR_NAME

# 📤 Copy Docker image and startup script to VM
echo "📤 Copying image and startup script to VM..."
gcloud compute scp $TAR_NAME start_container.sh "$instance_name:~" --zone="$zone"

# 🚀 Run the startup script remotely
echo "🚀 Running startup script on VM..."
gcloud compute ssh "$instance_name" --zone="$zone" --command="bash start_container.sh"
#!/bin/bash

set -e  # Exit immediately on error

read -p "Enter the instance name:  " instance_name
read -p "Enter the zone: " zone

# Define image name
IMAGE_NAME="pyvrp_docker_uploadable"
TAR_NAME="$IMAGE_NAME.tar"

# 🐳 Build Docker image with no cache
echo "🚧 Building Docker image with --no-cache..."
docker build --no-cache --pull -t $IMAGE_NAME .

# 💾 Save Docker image as .tar file
echo "💾 Saving image to $TAR_NAME..."
docker save $IMAGE_NAME -o $TAR_NAME

# 📤 Copy Docker image and startup script to VM
echo "📤 Copying image and startup script to VM..."
gcloud compute scp $TAR_NAME start_container.sh "$instance_name:~" --zone="$zone"

# 🚀 Run the startup script remotely
echo "🚀 Running startup script on VM..."
gcloud compute ssh "$instance_name" --zone="$zone" --command="bash start_container.sh"

