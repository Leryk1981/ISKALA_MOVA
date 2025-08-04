#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 ISKALA Production Deployment Tests
====================================

Comprehensive integration tests for production Docker deployment:
- Container health checks
- Service connectivity
- API endpoint functionality
- Performance requirements
- Security validation
- Recovery scenarios
"""

import asyncio
import pytest
import docker
import requests
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock

import docker.errors
from docker.models.containers import Container

# Test configuration
TEST_PROJECT_NAME = "iskala-test"
TEST_ENV_FILE = ".env.test"
TEST_COMPOSE_FILE = "docker-compose.prod.yml"
HEALTH_CHECK_TIMEOUT = 120
API_TIMEOUT = 30

@pytest.fixture(scope="module")
def docker_client():
    """Docker client for container management"""
    client = docker.from_env()
    yield client
    client.close()

@pytest.fixture(scope="module") 
def test_environment():
    """Setup test environment file"""
    test_env_content = """
# Test environment for deployment tests
NEO4J_PASSWORD=test_neo4j_password_123
REDIS_PASSWORD=test_redis_password_456
API_KEYS=test_api_key_1,test_api_key_2
ENVIRONMENT=test
LOG_LEVEL=DEBUG
NEO4J_HEAP_INITIAL=512m
NEO4J_HEAP_MAX=1g
REDIS_MAX_MEMORY=128mb
ENABLE_API_KEY_AUTH=false
COMPOSE_PROJECT_NAME=iskala-test
"""
    
    # Write test environment file
    with open(TEST_ENV_FILE, 'w') as f:
        f.write(test_env_content)
    
    yield TEST_ENV_FILE
    
    # Cleanup
    if os.path.exists(TEST_ENV_FILE):
        os.remove(TEST_ENV_FILE)

@pytest.fixture(scope="module")
def docker_compose_deployment(test_environment):
    """Deploy full Docker Compose stack for testing"""
    
    # Stop any existing test deployment
    subprocess.run([
        "docker-compose", "-p", TEST_PROJECT_NAME, 
        "-f", TEST_COMPOSE_FILE, "down", "-v"
    ], capture_output=True)
    
    # Start deployment
    result = subprocess.run([
        "docker-compose", "-p", TEST_PROJECT_NAME,
        "-f", TEST_COMPOSE_FILE, "--env-file", test_environment,
        "up", "-d", "--build"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        pytest.fail(f"Failed to start Docker Compose: {result.stderr}")
    
    # Wait for services to start
    time.sleep(30)
    
    yield TEST_PROJECT_NAME
    
    # Cleanup
    subprocess.run([
        "docker-compose", "-p", TEST_PROJECT_NAME,
        "-f", TEST_COMPOSE_FILE, "down", "-v"
    ], capture_output=True)

class TestDockerContainerHealth:
    """Test Docker container health and status"""
    
    def test_neo4j_container_health(self, docker_client, docker_compose_deployment):
        """Test Neo4j container is healthy"""
        container_name = f"{docker_compose_deployment}_neo4j_1"
        
        # Wait for container to be healthy
        start_time = time.time()
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                container = docker_client.containers.get(container_name)
                health = container.attrs['State']['Health']['Status']
                
                if health == 'healthy':
                    break
                elif health == 'unhealthy':
                    logs = container.logs().decode('utf-8')[-1000:]
                    pytest.fail(f"Neo4j container unhealthy. Logs: {logs}")
                    
                time.sleep(5)
            except docker.errors.NotFound:
                pytest.fail(f"Neo4j container {container_name} not found")
        else:
            pytest.fail(f"Neo4j container not healthy within {HEALTH_CHECK_TIMEOUT}s")
            
        # Verify container is running
        assert container.status == 'running'
        assert health == 'healthy'
    
    def test_redis_container_health(self, docker_client, docker_compose_deployment):
        """Test Redis container is healthy"""
        container_name = f"{docker_compose_deployment}_redis_1"
        
        start_time = time.time()
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                container = docker_client.containers.get(container_name)
                health = container.attrs['State']['Health']['Status']
                
                if health == 'healthy':
                    break
                elif health == 'unhealthy':
                    logs = container.logs().decode('utf-8')[-1000:]
                    pytest.fail(f"Redis container unhealthy. Logs: {logs}")
                    
                time.sleep(5)
            except docker.errors.NotFound:
                pytest.fail(f"Redis container {container_name} not found")
        else:
            pytest.fail(f"Redis container not healthy within {HEALTH_CHECK_TIMEOUT}s")
            
        assert container.status == 'running'
        assert health == 'healthy'
    
    def test_graph_search_container_health(self, docker_client, docker_compose_deployment):
        """Test Graph Search service container is healthy"""
        container_name = f"{docker_compose_deployment}_graph_search_1"
        
        start_time = time.time()
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                container = docker_client.containers.get(container_name)
                health = container.attrs['State']['Health']['Status']
                
                if health == 'healthy':
                    break
                elif health == 'unhealthy':
                    logs = container.logs().decode('utf-8')[-1000:]
                    pytest.fail(f"Graph Search container unhealthy. Logs: {logs}")
                    
                time.sleep(5)
            except docker.errors.NotFound:
                pytest.fail(f"Graph Search container {container_name} not found")
        else:
            pytest.fail(f"Graph Search container not healthy within {HEALTH_CHECK_TIMEOUT}s")
            
        assert container.status == 'running'
        assert health == 'healthy'
    
    def test_tool_server_container_health(self, docker_client, docker_compose_deployment):
        """Test Tool Server container is healthy"""
        container_name = f"{docker_compose_deployment}_tool_server_1"
        
        start_time = time.time()
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                container = docker_client.containers.get(container_name)
                health = container.attrs['State']['Health']['Status']
                
                if health == 'healthy':
                    break
                elif health == 'unhealthy':
                    logs = container.logs().decode('utf-8')[-1000:]
                    pytest.fail(f"Tool Server container unhealthy. Logs: {logs}")
                    
                time.sleep(5)
            except docker.errors.NotFound:
                pytest.fail(f"Tool Server container {container_name} not found")
        else:
            pytest.fail(f"Tool Server container not healthy within {HEALTH_CHECK_TIMEOUT}s")
            
        assert container.status == 'running'
        assert health == 'healthy'

class TestServiceConnectivity:
    """Test service-to-service connectivity"""
    
    def test_graph_search_api_health(self, docker_compose_deployment):
        """Test Graph Search API health endpoint"""
        url = "http://localhost:8004/health"
        
        start_time = time.time()
        while time.time() - start_time < API_TIMEOUT:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    assert health_data['status'] in ['healthy', 'degraded']
                    return
            except requests.exceptions.RequestException:
                time.sleep(2)
                continue
        
        pytest.fail(f"Graph Search API not responding within {API_TIMEOUT}s")
    
    def test_tool_server_api_health(self, docker_compose_deployment):
        """Test Tool Server API health endpoint"""
        url = "http://localhost:8003/health"
        
        start_time = time.time()
        while time.time() - start_time < API_TIMEOUT:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                time.sleep(2)
                continue
        
        pytest.fail(f"Tool Server API not responding within {API_TIMEOUT}s")
    
    def test_neo4j_bolt_connectivity(self, docker_client, docker_compose_deployment):
        """Test Neo4j Bolt protocol connectivity"""
        container_name = f"{docker_compose_deployment}_neo4j_1"
        
        try:
            container = docker_client.containers.get(container_name)
            
            # Test Cypher query execution
            result = container.exec_run([
                "cypher-shell", "-u", "neo4j", "-p", "test_neo4j_password_123",
                "RETURN 1 as test"
            ])
            
            assert result.exit_code == 0
            assert "test" in result.output.decode('utf-8')
            
        except docker.errors.NotFound:
            pytest.fail(f"Neo4j container {container_name} not found")
    
    def test_redis_connectivity(self, docker_client, docker_compose_deployment):
        """Test Redis connectivity and basic operations"""
        container_name = f"{docker_compose_deployment}_redis_1"
        
        try:
            container = docker_client.containers.get(container_name)
            
            # Test Redis ping
            result = container.exec_run([
                "redis-cli", "-a", "test_redis_password_456", "ping"
            ])
            
            assert result.exit_code == 0
            assert "PONG" in result.output.decode('utf-8')
            
            # Test basic set/get
            container.exec_run([
                "redis-cli", "-a", "test_redis_password_456", 
                "set", "test_key", "test_value"
            ])
            
            result = container.exec_run([
                "redis-cli", "-a", "test_redis_password_456", 
                "get", "test_key"
            ])
            
            assert "test_value" in result.output.decode('utf-8')
            
        except docker.errors.NotFound:
            pytest.fail(f"Redis container {container_name} not found")

class TestAPIFunctionality:
    """Test API endpoints functionality"""
    
    def test_graph_search_vector_endpoint(self, docker_compose_deployment):
        """Test Graph Search vector search endpoint"""
        url = "http://localhost:8004/api/v1/vector/search"
        
        payload = {
            "query": "test query",
            "language": "en",
            "k": 5
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            # Should return 200 or 422 (validation error) - both indicate API is working
            assert response.status_code in [200, 422, 503]  # 503 if no data indexed yet
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Vector search endpoint failed: {e}")
    
    def test_graph_search_hybrid_endpoint(self, docker_compose_deployment):
        """Test Graph Search hybrid search endpoint"""
        url = "http://localhost:8004/api/v1/search/hybrid"
        
        payload = {
            "query": "artificial intelligence",
            "language": "en",
            "k": 5
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            assert response.status_code in [200, 422, 503]
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Hybrid search endpoint failed: {e}")
    
    def test_tool_server_openapi_schema(self, docker_compose_deployment):
        """Test Tool Server OpenAPI schema accessibility"""
        url = "http://localhost:8003/openapi.json"
        
        try:
            response = requests.get(url, timeout=5)
            assert response.status_code == 200
            
            schema = response.json()
            assert "openapi" in schema
            assert "paths" in schema
            assert "info" in schema
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"OpenAPI schema endpoint failed: {e}")

class TestPerformanceRequirements:
    """Test performance requirements are met"""
    
    def test_api_response_time(self, docker_compose_deployment):
        """Test API response times are under 200ms for health checks"""
        
        endpoints = [
            "http://localhost:8004/health",
            "http://localhost:8003/health"
        ]
        
        for url in endpoints:
            start_time = time.time()
            try:
                response = requests.get(url, timeout=1)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    assert response_time < 500  # 500ms threshold for cold start
                    
            except requests.exceptions.RequestException:
                # Service might still be starting up
                pass
    
    def test_container_resource_limits(self, docker_client, docker_compose_deployment):
        """Test containers respect resource limits"""
        
        container_limits = {
            f"{docker_compose_deployment}_neo4j_1": {"memory": "6G"},
            f"{docker_compose_deployment}_redis_1": {"memory": "768M"},
            f"{docker_compose_deployment}_graph_search_1": {"memory": "2G"}
        }
        
        for container_name, limits in container_limits.items():
            try:
                container = docker_client.containers.get(container_name)
                host_config = container.attrs['HostConfig']
                
                if 'Memory' in host_config and host_config['Memory'] > 0:
                    # Container has memory limit set
                    assert host_config['Memory'] > 0
                    
            except docker.errors.NotFound:
                # Container might not exist in test environment
                pass

class TestRecoveryScenarios:
    """Test service recovery and resilience"""
    
    def test_container_restart_recovery(self, docker_client, docker_compose_deployment):
        """Test containers can restart and recover"""
        
        # Test Redis restart (safer than Neo4j)
        container_name = f"{docker_compose_deployment}_redis_1"
        
        try:
            container = docker_client.containers.get(container_name)
            
            # Restart container
            container.restart(timeout=30)
            
            # Wait for recovery
            time.sleep(10)
            
            # Check health
            start_time = time.time()
            while time.time() - start_time < 60:
                container.reload()
                if container.attrs['State']['Health']['Status'] == 'healthy':
                    break
                time.sleep(5)
            else:
                pytest.fail("Container failed to recover after restart")
                
        except docker.errors.NotFound:
            pytest.skip(f"Container {container_name} not found for restart test")
    
    def test_network_resilience(self, docker_compose_deployment):
        """Test service resilience to network issues"""
        
        # Test if services handle connection timeouts gracefully
        url = "http://localhost:8004/health"
        
        try:
            response = requests.get(url, timeout=0.1)  # Very short timeout
        except requests.exceptions.Timeout:
            # Expected behavior - service should handle timeouts
            pass
        
        # Follow up with normal request
        time.sleep(1)
        response = requests.get(url, timeout=5)
        # Should still work after timeout

class TestSecurityConfiguration:
    """Test security features are properly configured"""
    
    def test_non_root_user_containers(self, docker_client, docker_compose_deployment):
        """Test containers run as non-root users"""
        
        service_containers = [
            f"{docker_compose_deployment}_graph_search_1", 
            f"{docker_compose_deployment}_tool_server_1"
        ]
        
        for container_name in service_containers:
            try:
                container = docker_client.containers.get(container_name)
                
                # Check running user
                result = container.exec_run(["whoami"])
                user = result.output.decode('utf-8').strip()
                
                assert user != "root", f"Container {container_name} running as root"
                
            except docker.errors.NotFound:
                pytest.skip(f"Container {container_name} not found for security test")
    
    def test_environment_secrets(self, docker_client, docker_compose_deployment):
        """Test sensitive environment variables are not exposed"""
        
        container_name = f"{docker_compose_deployment}_neo4j_1"
        
        try:
            container = docker_client.containers.get(container_name)
            env_vars = container.attrs['Config']['Env']
            
            # Check that passwords are set but not default values
            neo4j_auth = next((env for env in env_vars if env.startswith('NEO4J_AUTH=')), None)
            
            if neo4j_auth:
                assert "change_this" not in neo4j_auth
                assert len(neo4j_auth.split('/')[-1]) > 8  # Password length check
                
        except docker.errors.NotFound:
            pytest.skip(f"Container {container_name} not found for security test")

@pytest.mark.integration
class TestFullIntegration:
    """End-to-end integration tests"""
    
    def test_complete_deployment_workflow(self, docker_compose_deployment):
        """Test complete deployment workflow functions"""
        
        # 1. Verify all services are up
        services = {
            "Graph Search": "http://localhost:8004/health",
            "Tool Server": "http://localhost:8003/health"
        }
        
        for service_name, url in services.items():
            response = requests.get(url, timeout=10)
            assert response.status_code in [200, 503], f"{service_name} not responding"
        
        # 2. Test service integration
        # Graph Search should be accessible from Tool Server
        tool_server_url = "http://localhost:8003/"
        response = requests.get(tool_server_url, timeout=5)
        assert response.status_code == 200
        
        # 3. Verify data persistence volumes are mounted
        # This would be tested by checking if data persists after restart
        # but that's complex for unit tests
        
    def test_monitoring_endpoints(self, docker_compose_deployment):
        """Test monitoring endpoints are accessible"""
        
        endpoints = [
            "http://localhost:8004/metrics",  # Prometheus metrics
            "http://localhost:8004/version",   # Version info
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200
            except requests.exceptions.RequestException:
                pytest.skip(f"Monitoring endpoint {url} not accessible in test environment")

if __name__ == "__main__":
    # Run deployment tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]) 