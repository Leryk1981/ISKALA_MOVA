#!/bin/bash
set -euo pipefail

# =====================================================
# ISKALA Production Deployment Script
# =====================================================
# Automated deployment with validation, health checks, and rollback support

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV="${DEPLOY_ENV:-production}"
ENV_FILE="${ENV_FILE:-.env.prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
PROJECT_NAME="${PROJECT_NAME:-iskala-prod}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-300}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-10}"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
echo -e "${PURPLE}"
cat << "EOF"
🚀 ISKALA Production Deployment Script
==========================================
   _____ _____ _  __          _               
  |_   _|  ___| |/ /   /\    | |    /\        
    | | | |_  | ' /   /  \   | |   /  \       
    | | |  _| |  <   / /\ \  | |  / /\ \      
   _| |_| |   | . \ / ____ \ | |_/ ____ \     
  |_____|_|   |_|\_\/_/    \_\|_____/    \_\  
                                              
Production Ready Docker Deployment
==========================================
EOF
echo -e "${NC}"

# Function to check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file $ENV_FILE not found"
        warn "Please copy env.prod.template to $ENV_FILE and configure it"
        exit 1
    fi
    
    # Check compose file
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    log "✅ All prerequisites satisfied"
}

# Function to validate environment configuration
validate_environment() {
    log "📋 Validating environment configuration..."
    
    # Source environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check critical passwords
    if [[ "${NEO4J_PASSWORD:-}" == *"change_this"* ]]; then
        error "Neo4j password still uses default value. Please update $ENV_FILE"
        exit 1
    fi
    
    if [[ "${REDIS_PASSWORD:-}" == *"change_this"* ]]; then
        error "Redis password still uses default value. Please update $ENV_FILE"
        exit 1
    fi
    
    # Validate Docker Compose configuration
    if ! docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config > /dev/null; then
        error "Docker Compose configuration validation failed"
        exit 1
    fi
    
    log "✅ Environment configuration validated"
}

# Function to create necessary directories
create_directories() {
    log "📁 Creating data directories..."
    
    # Create data directories with proper permissions
    sudo mkdir -p /opt/iskala/data/{neo4j/{data,logs,import,plugins,conf},redis}
    sudo chown -R 7474:7474 /opt/iskala/data/neo4j  # Neo4j user
    sudo chown -R 999:999 /opt/iskala/data/redis    # Redis user
    
    # Create local directories
    mkdir -p ./data/{neo4j/{data,logs},redis}
    mkdir -p ./logs/{graph_search,tool_server}
    mkdir -p ./monitoring/{prometheus,grafana,alertmanager}
    
    log "✅ Data directories created"
}

# Function to backup existing deployment
backup_existing() {
    log "💾 Creating backup of existing deployment..."
    
    BACKUP_DIR="./backups/$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$BACKUP_DIR"
    
    # Backup environment file
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$BACKUP_DIR/"
    fi
    
    # Export current container configurations
    if docker-compose -p "$PROJECT_NAME" ps -q &> /dev/null; then
        docker-compose -p "$PROJECT_NAME" config > "$BACKUP_DIR/docker-compose.backup.yml"
        info "💾 Backup created at $BACKUP_DIR"
    else
        info "💾 No existing deployment to backup"
    fi
}

# Function to build Docker images
build_images() {
    log "🏗️ Building Docker images..."
    
    # Build images with no cache for production
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache --parallel
    
    # Tag images with build metadata
    BUILD_VERSION=$(grep "BUILD_VERSION=" "$ENV_FILE" | cut -d'=' -f2)
    BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    BUILD_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    info "🏗️ Images built successfully"
    info "   Version: $BUILD_VERSION"
    info "   Date: $BUILD_DATE"
    info "   Commit: $BUILD_COMMIT"
}

# Function to stop existing services gracefully
stop_services() {
    log "🛑 Stopping existing services..."
    
    if docker-compose -p "$PROJECT_NAME" ps -q &> /dev/null; then
        # Graceful shutdown with timeout
        docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" stop -t 30
        docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down --remove-orphans
        info "🛑 Existing services stopped"
    else
        info "🛑 No existing services to stop"
    fi
}

# Function to start services
start_services() {
    log "🚀 Starting ISKALA production services..."
    
    # Start services with timeout
    timeout $TIMEOUT_SECONDS docker-compose \
        -p "$PROJECT_NAME" \
        -f "$COMPOSE_FILE" \
        --env-file "$ENV_FILE" \
        up -d --remove-orphans
    
    log "✅ Services started successfully"
}

# Function to wait for services to be healthy
wait_for_health() {
    log "🩺 Waiting for services to be healthy..."
    
    local services=("neo4j" "redis" "graph_search" "tool_server")
    local max_retries=$HEALTH_CHECK_RETRIES
    local retry=0
    
    while [[ $retry -lt $max_retries ]]; do
        local all_healthy=true
        
        for service in "${services[@]}"; do
            local health_status
            health_status=$(docker-compose -p "$PROJECT_NAME" ps -q "$service" | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "no_health")
            
            if [[ "$health_status" != "healthy" ]]; then
                all_healthy=false
                info "⏳ Waiting for $service to be healthy (status: $health_status)"
                break
            fi
        done
        
        if [[ "$all_healthy" == true ]]; then
            log "✅ All services are healthy"
            return 0
        fi
        
        retry=$((retry + 1))
        sleep 10
    done
    
    error "❌ Services failed to become healthy within timeout"
    return 1
}

# Function to run smoke tests
run_smoke_tests() {
    log "🌪️ Running smoke tests..."
    
    # Test Graph Search service
    if curl -f http://localhost:8004/health &> /dev/null; then
        log "✅ Graph Search service responding"
    else
        error "❌ Graph Search service not responding"
        return 1
    fi
    
    # Test Tool Server
    if curl -f http://localhost:8003/health &> /dev/null; then
        log "✅ Tool Server responding"
    else
        error "❌ Tool Server not responding" 
        return 1
    fi
    
    # Test Neo4j connectivity
    if docker-compose -p "$PROJECT_NAME" exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1" &> /dev/null; then
        log "✅ Neo4j database accessible"
    else
        error "❌ Neo4j database not accessible"
        return 1
    fi
    
    # Test Redis connectivity
    if docker-compose -p "$PROJECT_NAME" exec -T redis redis-cli -a "$REDIS_PASSWORD" ping | grep -q PONG; then
        log "✅ Redis cache accessible"
    else
        error "❌ Redis cache not accessible"
        return 1
    fi
    
    log "✅ All smoke tests passed"
}

# Function to display deployment status
show_status() {
    log "📊 Deployment Status"
    echo "============================================"
    
    # Show service status
    docker-compose -p "$PROJECT_NAME" ps
    
    echo ""
    info "🔗 Service Endpoints:"
    echo "   Graph Search API:  http://localhost:8004"
    echo "   Tool Server API:   http://localhost:8003"  
    echo "   Neo4j Browser:     http://localhost:7474"
    echo "   Redis:             localhost:6379"
    
    if docker-compose -p "$PROJECT_NAME" ps | grep -q prometheus; then
        echo "   Prometheus:        http://localhost:9090"
        echo "   Grafana:           http://localhost:3000"
    fi
    
    echo ""
    info "📋 Management Commands:"
    echo "   View logs:    docker-compose -p $PROJECT_NAME logs -f"
    echo "   Stop all:     docker-compose -p $PROJECT_NAME down"
    echo "   Restart:      docker-compose -p $PROJECT_NAME restart"
    echo "   Scale up:     docker-compose -p $PROJECT_NAME up -d --scale graph_search=3"
}

# Function to rollback deployment
rollback() {
    error "❌ Deployment failed. Initiating rollback..."
    
    # Stop current deployment
    docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down --remove-orphans || true
    
    # Try to start previous version if backup exists
    LATEST_BACKUP=$(ls -t ./backups/ 2>/dev/null | head -n1)
    if [[ -n "$LATEST_BACKUP" ]] && [[ -f "./backups/$LATEST_BACKUP/docker-compose.backup.yml" ]]; then
        warn "🔄 Rolling back to previous version..."
        docker-compose -f "./backups/$LATEST_BACKUP/docker-compose.backup.yml" up -d || true
    fi
    
    error "💥 Deployment failed and rollback attempted"
    exit 1
}

# Main deployment function
main() {
    log "🚀 Starting ISKALA production deployment..."
    
    # Trap errors for rollback
    trap rollback ERR
    
    # Run deployment steps
    check_prerequisites
    validate_environment
    create_directories
    backup_existing
    build_images
    stop_services
    start_services
    
    # Wait for services and test
    if wait_for_health && run_smoke_tests; then
        show_status
        
        echo ""
        log "🎉 ISKALA Production Deployment Completed Successfully!"
        log "🚀 All services are running and healthy"
        log "📊 Monitor deployment with: docker-compose -p $PROJECT_NAME logs -f"
        
        return 0
    else
        rollback
    fi
}

# Command line options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        log "🔄 Manual rollback requested..."
        rollback
        ;;
    "status")
        show_status
        ;;
    "stop")
        log "🛑 Stopping all services..."
        docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down
        ;;
    "logs")
        docker-compose -p "$PROJECT_NAME" logs -f
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [deploy|rollback|status|stop|logs|help]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy ISKALA production environment (default)"
        echo "  rollback - Rollback to previous deployment"
        echo "  status   - Show current deployment status"
        echo "  stop     - Stop all services"
        echo "  logs     - Show service logs"
        echo "  help     - Show this help message"
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac 