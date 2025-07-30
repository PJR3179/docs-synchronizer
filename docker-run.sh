#!/bin/bash

# MD2Conf Docker Helper Script - helps to build and run the MD2Conf API in Docker with Rancher support

set -e

# Check for required environment variables
RANCHER_URL=${RANCHER_URL:-""}
RANCHER_ACCESS_KEY=${RANCHER_ACCESS_KEY:-""}
RANCHER_SECRET_KEY=${RANCHER_SECRET_KEY:-""}
RANCHER_PROJECT=${RANCHER_PROJECT:-""}

# Functions
show_help() {
  echo "MD2Conf Docker Helper Script with Rancher Support"
  echo ""
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  build       Build the Docker image"
  echo "  run         Run the container (builds first if needed)"
  echo "  stop        Stop the running container"
  echo "  restart     Restart the container"
  echo "  logs        Show container logs"
  echo "  shell       Open a shell in the running container"
  echo "  test        Test the API with a sample request"
  echo "  help        Show this help message"
  echo ""
  echo "Rancher Support:"
  echo "  To deploy to Rancher, set these environment variables:"
  echo "  - RANCHER_URL          - Your Rancher server URL"
  echo "  - RANCHER_ACCESS_KEY   - Rancher API access key"
  echo "  - RANCHER_SECRET_KEY   - Rancher API secret key"
  echo "  - RANCHER_PROJECT      - Target project (optional)"
  echo ""
  echo "  Example:"
  echo "  export RANCHER_URL=https://rancher.example.com"
  echo "  export RANCHER_ACCESS_KEY=token-abc123"
  echo "  export RANCHER_SECRET_KEY=secretkey456"
  echo "  export RANCHER_PROJECT=default"
  echo "  ./docker-run.sh run"
  echo ""
}

build_image() {
  echo "Building Docker image..."
  docker build -t md2conf-api .
  
  # If Rancher environment variables are set, push to Rancher registry
  if [[ -n "$RANCHER_URL" && -n "$RANCHER_ACCESS_KEY" && -n "$RANCHER_SECRET_KEY" ]]; then
    echo "Pushing image to Rancher registry..."
    
    # Login to Rancher private registry if specified
    REGISTRY_URL=$(echo $RANCHER_URL | sed 's/^https*:\/\///')
    if [[ -n "$REGISTRY_URL" ]]; then
      docker tag md2conf-api $REGISTRY_URL/md2conf-api:latest
      docker login $REGISTRY_URL --username $RANCHER_ACCESS_KEY --password $RANCHER_SECRET_KEY
      docker push $REGISTRY_URL/md2conf-api:latest
      echo "Image pushed to Rancher registry at $REGISTRY_URL"
    fi
  fi
  
  echo "Image built successfully!"
}

run_container() {
  # Check if we're using Rancher
  if [[ -n "$RANCHER_URL" && -n "$RANCHER_ACCESS_KEY" && -n "$RANCHER_SECRET_KEY" ]]; then
    run_in_rancher
    return
  fi
  
  # Local Docker deployment
  # Check if image exists, build if it doesn't
  if [[ "$(docker images -q md2conf-api 2> /dev/null)" == "" ]]; then
    build_image
  fi
  
  # Check if container is already running
  if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" != "" ]]; then
    echo "Container is already running. Use 'restart' to restart it."
    return
  fi
  
  # Check if .env file exists
  if [[ -f .env ]]; then
    echo "Found .env file, using environment variables from it."
    docker run -d --name md2conf-api -p 8000:8000 --env-file .env -v $(pwd)/docs:/app/docs md2conf-api
  else
    echo "No .env file found. Using default configuration."
    echo "You may need to provide Confluence credentials in API requests."
    docker run -d --name md2conf-api -p 8000:8000 -v $(pwd)/docs:/app/docs md2conf-api
  fi
  
  echo "Container started. API available at http://localhost:8000"
}

stop_container() {
  # Check if we're using Rancher
  if [[ -n "$RANCHER_URL" && -n "$RANCHER_ACCESS_KEY" && -n "$RANCHER_SECRET_KEY" ]]; then
    stop_in_rancher
    return
  fi
  
  # Local Docker stop
  if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" != "" ]]; then
    echo "Stopping container..."
    docker stop md2conf-api
    docker rm md2conf-api
    echo "Container stopped and removed."
  else
    echo "No running container found."
  fi
}

restart_container() {
  stop_container
  run_container
}

show_logs() {
  # Check if we're using Rancher
  if [[ -n "$RANCHER_URL" && -n "$RANCHER_ACCESS_KEY" && -n "$RANCHER_SECRET_KEY" ]]; then
    if check_rancher_cli && setup_rancher_cli; then
      echo "Showing logs from Rancher deployment..."
      rancher kubectl logs -f deployment/md2conf-api
    else
      echo "Cannot access Rancher logs without CLI setup."
    fi
  else
    # Local Docker logs
    if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" != "" ]]; then
      docker logs -f md2conf-api
    else
      echo "No running container found."
    fi
  fi
}

open_shell() {
  # Check if we're using Rancher
  if [[ -n "$RANCHER_URL" && -n "$RANCHER_ACCESS_KEY" && -n "$RANCHER_SECRET_KEY" ]]; then
    if check_rancher_cli && setup_rancher_cli; then
      echo "Opening shell in Rancher pod..."
      POD_NAME=$(rancher kubectl get pods -l run=md2conf-api -o jsonpath='{.items[0].metadata.name}')
      if [[ -n "$POD_NAME" ]]; then
        rancher kubectl exec -it $POD_NAME -- bash
      else
        echo "No md2conf-api pod found in Rancher."
      fi
    else
      echo "Cannot open shell without Rancher CLI setup."
    fi
  else
    # Local Docker shell
    if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" != "" ]]; then
      docker exec -it md2conf-api bash
    else
      echo "No running container found."
    fi
  fi
}

test_api() {
  if [[ -n "$RANCHER_URL" ]]; then
    # For Rancher, we need to check the service endpoint
    echo "Testing API health endpoint on Rancher..."
    SERVICE_URL=$(get_rancher_service_url)
    if [[ -n "$SERVICE_URL" ]]; then
      curl -s $SERVICE_URL/health | jq .
    else
      echo "Cannot determine Rancher service URL. Is the service running?"
    fi
  else
    # Local Docker test
    if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" == "" ]]; then
      echo "Container is not running. Starting it..."
      run_container
      
      # Wait for container to start with retry logic
      echo "Waiting for container to be ready..."
      max_retries=3
      retry_count=0
      container_ready=false
      
      while [[ $retry_count -lt $max_retries && $container_ready == false ]]; do
        retry_count=$((retry_count + 1))
        echo "Attempt $retry_count of $max_retries: Waiting 5 seconds for container to start..."
        sleep 5
        
        # Check if container is running and responding
        if [[ "$(docker ps -q -f name=md2conf-api 2> /dev/null)" != "" ]]; then
          # Test if the health endpoint is responding
          if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            container_ready=true
            echo "Container is ready!"
          else
            echo "Container is running but not responding to health check yet..."
          fi
        else
          echo "Container not running yet..."
        fi
      done
      
      if [[ $container_ready == false ]]; then
        echo "Warning: Container may not be fully ready after $max_retries attempts."
        echo "Proceeding with API test anyway..."
      fi
    fi
    
    echo "Testing API health endpoint..."
    curl -s http://localhost:8000/health | jq .
  fi
}

# Rancher specific functions
check_rancher_cli() {
  if ! command -v rancher &> /dev/null; then
    echo "Rancher CLI not found. Please install it first:"
    echo "https://rancher.com/docs/rancher/v2.x/en/cli/"
    return 1
  fi
  return 0
}

setup_rancher_cli() {
  if [[ -z "$RANCHER_URL" || -z "$RANCHER_ACCESS_KEY" || -z "$RANCHER_SECRET_KEY" ]]; then
    echo "Error: Rancher environment variables not set."
    echo "Please set RANCHER_URL, RANCHER_ACCESS_KEY, RANCHER_SECRET_KEY, and RANCHER_PROJECT"
    return 1
  fi
  
  # Configure Rancher CLI
  rancher login "$RANCHER_URL" --token "$RANCHER_ACCESS_KEY:$RANCHER_SECRET_KEY" --context "$RANCHER_PROJECT"
  if [ $? -ne 0 ]; then
    echo "Failed to log in to Rancher. Please check your credentials."
    return 1
  fi
  return 0
}

run_in_rancher() {
  echo "Deploying to Rancher..."
  
  # Check for Rancher CLI
  if ! check_rancher_cli; then
    echo "Attempting API-based deployment instead..."
    deploy_via_rancher_api
    return
  fi
  
  # Setup Rancher CLI
  if ! setup_rancher_cli; then
    return 1
  fi
  
  # Check if .env file exists for environment variables
  ENV_VARS=""
  if [[ -f .env ]]; then
    echo "Found .env file, using environment variables from it."
    while IFS= read -r line || [[ -n "$line" ]]; do
      # Skip comments and empty lines
      [[ $line =~ ^#.*$ || -z "$line" ]] && continue
      ENV_VARS="$ENV_VARS --env $(echo $line | tr -d '\r')"
    done < .env
  fi
  
  # Build and push image if needed
  build_image
  
  # Deploy or update the workload
  if rancher apps ls | grep -q md2conf-api; then
    echo "Updating existing md2conf-api deployment..."
    rancher kubectl rollout restart deployment md2conf-api
  else
    echo "Creating new md2conf-api deployment..."
    # Create workload with the image
    REGISTRY_URL=$(echo $RANCHER_URL | sed 's/^https*:\/\///')
    IMAGE_NAME="$REGISTRY_URL/md2conf-api:latest"
    
    rancher kubectl run md2conf-api \
      --image=$IMAGE_NAME \
      --port=8000 \
      $ENV_VARS
      
    # Expose the service
    rancher kubectl expose deployment md2conf-api --port=8000 --type=ClusterIP
  fi
  
  echo "Deployment to Rancher completed."
  echo "Service URL: $(get_rancher_service_url)"
}

deploy_via_rancher_api() {
  echo "API-based Rancher deployment not implemented yet."
  echo "Please install Rancher CLI for the best experience."
  echo "Visit: https://rancher.com/docs/rancher/v2.x/en/cli/"
}

get_rancher_service_url() {
  if check_rancher_cli && setup_rancher_cli; then
    # Get the service URL
    SERVICE_IP=$(rancher kubectl get service md2conf-api -o jsonpath='{.spec.clusterIP}')
    if [[ -n "$SERVICE_IP" ]]; then
      echo "http://$SERVICE_IP:8000"
      return 0
    fi
  fi
  echo ""
  return 1
}

stop_in_rancher() {
  echo "Stopping service in Rancher..."
  
  if ! check_rancher_cli || ! setup_rancher_cli; then
    return 1
  fi
  
  if rancher apps ls | grep -q md2conf-api; then
    rancher kubectl delete deployment md2conf-api
    rancher kubectl delete service md2conf-api
    echo "md2conf-api service stopped and removed from Rancher."
  else
    echo "No md2conf-api service found in Rancher."
  fi
}

# Main script
case "$1" in
  build)
    build_image
    ;;
  run)
    run_container
    ;;
  stop)
    stop_container
    ;;
  restart)
    restart_container
    ;;
  logs)
    show_logs
    ;;
  shell)
    open_shell
    ;;
  test)
    test_api
    ;;
  help|--help|-h|"")
    show_help
    ;;
  *)
    echo "Unknown command: $1"
    show_help
    exit 1
    ;;
esac
