"""
🔧 Integration Handler for ISKALA Tool Server
Handles the integration of Graph Search capabilities into existing Tool Server

This module provides:
- Functions to extend existing iskala_openapi_server.py
- Endpoint registration
- OpenAPI schema updates
- Backward compatibility maintenance
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to Python path for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from iskala_graph_integration.adapters.tool_server_extension import (
    graph_extension,
    get_graph_search_openapi_extensions
)
from iskala_graph_integration.schemas.requests import (
    GraphHybridSearchRequest,
    GraphVectorSearchRequest,
    GraphWalkRequest,
    GraphSuggestionsRequest
)

logger = logging.getLogger(__name__)

class ToolServerIntegrationHandler:
    """
    🔧 Handler for integrating Graph Search into ISKALA Tool Server
    
    This class provides methods to:
    - Extend existing OpenAPI schema
    - Add new endpoints to FastAPI app
    - Maintain backward compatibility
    - Handle integration lifecycle
    """
    
    def __init__(self, app=None, openapi_schema=None):
        self.app = app
        self.openapi_schema = openapi_schema or {}
        self.is_integrated = False
        
        logger.info("🔧 Tool Server Integration Handler initialized")
    
    def integrate_graph_search_endpoints(self, app, openapi_schema: Dict[str, Any]):
        """
        Integrate Graph Search endpoints into existing FastAPI app and OpenAPI schema
        
        Args:
            app: FastAPI application instance
            openapi_schema: Current OpenAPI schema dictionary
        """
        try:
            logger.info("🚀 Starting Graph Search integration...")
            
            # 1. Add new endpoints to FastAPI app
            self._add_graph_search_endpoints(app)
            
            # 2. Extend OpenAPI schema
            self._extend_openapi_schema(openapi_schema)
            
            # 3. Update schema info
            self._update_schema_info(openapi_schema)
            
            self.is_integrated = True
            logger.info("✅ Graph Search integration completed successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Graph Search integration failed: {e}")
            return False
    
    def _add_graph_search_endpoints(self, app):
        """Add Graph Search endpoints to FastAPI app"""
        
        @app.post("/iskala/graph/search_hybrid")
        async def graph_search_hybrid(request: GraphHybridSearchRequest):
            """Гібридний семантичний пошук (векторний + графовий)"""
            try:
                return await graph_extension.hybrid_search(request)
            except Exception as e:
                logger.error(f"❌ Hybrid search error: {e}")
                raise
        
        @app.post("/iskala/graph/search_vector")
        async def graph_search_vector(request: GraphVectorSearchRequest):
            """Векторний семантичний пошук"""
            try:
                return await graph_extension.vector_search(request)
            except Exception as e:
                logger.error(f"❌ Vector search error: {e}")
                raise
        
        @app.post("/iskala/graph/walk")
        async def graph_walk(request: GraphWalkRequest):
            """Обхід графа знань для пошуку пов'язаних концептів"""
            try:
                return await graph_extension.graph_walk(request)
            except Exception as e:
                logger.error(f"❌ Graph walk error: {e}")
                raise
        
        @app.post("/iskala/graph/suggestions")
        async def graph_suggestions(request: GraphSuggestionsRequest):
            """Інтелектуальні підказки для пошукових запитів"""
            try:
                return await graph_extension.search_suggestions(request)
            except Exception as e:
                logger.error(f"❌ Graph suggestions error: {e}")
                raise
        
        @app.get("/iskala/graph/status")
        async def graph_status():
            """Статус Graph Search сервісу та компонентів"""
            try:
                return await graph_extension.get_status()
            except Exception as e:
                logger.error(f"❌ Graph status error: {e}")
                raise
        
        logger.info("✅ Graph Search endpoints added to FastAPI app")
    
    def _extend_openapi_schema(self, openapi_schema: Dict[str, Any]):
        """Extend existing OpenAPI schema with Graph Search paths"""
        
        # Get Graph Search OpenAPI extensions
        graph_extensions = get_graph_search_openapi_extensions()
        
        # Add new paths to existing schema
        if "paths" not in openapi_schema:
            openapi_schema["paths"] = {}
        
        openapi_schema["paths"].update(graph_extensions)
        
        logger.info(f"✅ OpenAPI schema extended with {len(graph_extensions)} Graph Search endpoints")
    
    def _update_schema_info(self, openapi_schema: Dict[str, Any]):
        """Update OpenAPI schema info to reflect Graph Search integration"""
        
        if "info" not in openapi_schema:
            openapi_schema["info"] = {}
        
        # Update description to mention Graph Search
        current_description = openapi_schema["info"].get("description", "")
        if "Graph Search" not in current_description:
            enhanced_description = (
                f"{current_description}\n\n"
                "🔍 **Graph Search Integration**: Розширено з можливостями семантичного пошуку:\n"
                "- Гібридний пошук (векторний + графовий)\n"
                "- Обхід графа знань\n"
                "- Інтелектуальні підказки\n"
                "- Мультимовна підтримка (50+ мов)"
            )
            openapi_schema["info"]["description"] = enhanced_description.strip()
        
        # Update version if needed
        current_version = openapi_schema["info"].get("version", "1.0.0")
        if "graph" not in current_version.lower():
            openapi_schema["info"]["version"] = f"{current_version}-graph"
        
        logger.info("✅ OpenAPI schema info updated")
    
    def generate_integration_code(self) -> str:
        """
        Generate Python code to integrate Graph Search into existing server
        
        Returns:
            String containing Python code for integration
        """
        
        integration_code = '''
# 🔍 ISKALA Graph Search Integration
# Auto-generated integration code for existing iskala_openapi_server.py

try:
    # Import Graph Search integration components
    from iskala_graph_integration.handlers.integration_handler import ToolServerIntegrationHandler
    from iskala_graph_integration.adapters.tool_server_extension import graph_extension
    
    # Initialize integration handler
    integration_handler = ToolServerIntegrationHandler()
    
    # Integrate Graph Search endpoints
    integration_success = integration_handler.integrate_graph_search_endpoints(app, OPENAPI_SCHEMA)
    
    if integration_success:
        print("✅ ISKALA Graph Search integration successful!")
        print("📋 New endpoints added:")
        print("   - POST /iskala/graph/search_hybrid - Гібридний семантичний пошук")
        print("   - POST /iskala/graph/search_vector - Векторний пошук")
        print("   - POST /iskala/graph/walk - Обхід графа знань")
        print("   - POST /iskala/graph/suggestions - Інтелектуальні підказки")
        print("   - GET /iskala/graph/status - Статус Graph Search")
        
        # Update root endpoint to include Graph Search endpoints
        @app.get("/")
        async def root():
            """Кореневий endpoint з Graph Search information"""
            return {
                "message": "ISKALA OpenAPI Tool Server with Graph Search",
                "version": "1.0.0-graph",
                "endpoints": {
                    # Existing endpoints
                    "openapi": "/openapi.json",
                    "memory_search": "/iskala/memory/search",
                    "tool_call": "/iskala/tools/call",
                    "translation": "/iskala/translation/translate",
                    "rag_search": "/iskala/rag/search",
                    "status": "/iskala/status",
                    
                    # New Graph Search endpoints
                    "graph_hybrid_search": "/iskala/graph/search_hybrid",
                    "graph_vector_search": "/iskala/graph/search_vector",
                    "graph_walk": "/iskala/graph/walk",
                    "graph_suggestions": "/iskala/graph/suggestions",
                    "graph_status": "/iskala/graph/status"
                },
                "graph_search": {
                    "enabled": True,
                    "features": [
                        "Hybrid semantic search (vector + graph)",
                        "Knowledge graph traversal",
                        "Intelligent search suggestions",
                        "Multilingual support (50+ languages)",
                        "Ukrainian language specialization"
                    ]
                }
            }
    else:
        print("❌ ISKALA Graph Search integration failed!")
        
except ImportError as e:
    print(f"⚠️ Graph Search integration not available: {e}")
    print("   Install iskala_graph_integration package to enable Graph Search features")
    
except Exception as e:
    print(f"❌ Graph Search integration error: {e}")
'''
        
        return integration_code
    
    def create_integrated_server_file(self, output_path: str = None) -> str:
        """
        Create a new integrated server file with Graph Search capabilities
        
        Args:
            output_path: Path where to save the integrated server file
            
        Returns:
            Path to the created file
        """
        
        if not output_path:
            output_path = "iskala_openapi_server_with_graph.py"
        
        try:
            # Read existing server file
            existing_server_path = Path(current_dir) / "iskala_openapi_server.py"
            
            if not existing_server_path.exists():
                raise FileNotFoundError(f"Existing server file not found: {existing_server_path}")
            
            with open(existing_server_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Generate integration code
            integration_code = self.generate_integration_code()
            
            # Find insertion point (before if __name__ == "__main__":)
            insertion_point = existing_content.find('if __name__ == "__main__":')
            
            if insertion_point == -1:
                # If no main block found, append at the end
                integrated_content = existing_content + "\n\n" + integration_code
            else:
                # Insert before main block
                integrated_content = (
                    existing_content[:insertion_point] + 
                    integration_code + "\n\n" + 
                    existing_content[insertion_point:]
                )
            
            # Write integrated file
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(integrated_content)
            
            logger.info(f"✅ Integrated server file created: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to create integrated server file: {e}")
            raise
    
    def verify_integration(self) -> Dict[str, Any]:
        """
        Verify that Graph Search integration is working correctly
        
        Returns:
            Dictionary with verification results
        """
        
        verification_results = {
            "integration_status": self.is_integrated,
            "graph_extension_available": graph_extension is not None,
            "endpoints_count": 0,
            "schema_extended": False,
            "errors": []
        }
        
        try:
            # Check if Graph Search extension is properly initialized
            if graph_extension:
                stats = graph_extension.get_performance_stats()
                verification_results["extension_stats"] = stats
            
            # Check OpenAPI schema extensions
            graph_extensions = get_graph_search_openapi_extensions()
            verification_results["endpoints_count"] = len(graph_extensions)
            verification_results["schema_extended"] = len(graph_extensions) > 0
            
            logger.info(f"✅ Integration verification completed: {verification_results}")
            
        except Exception as e:
            verification_results["errors"].append(str(e))
            logger.error(f"❌ Integration verification error: {e}")
        
        return verification_results

# Convenience functions for easy integration

def quick_integrate_graph_search(app, openapi_schema: Dict[str, Any]) -> bool:
    """
    Quick integration function for Graph Search
    
    Args:
        app: FastAPI application
        openapi_schema: OpenAPI schema dictionary
        
    Returns:
        True if integration successful, False otherwise
    """
    handler = ToolServerIntegrationHandler()
    return handler.integrate_graph_search_endpoints(app, openapi_schema)

def create_graph_enhanced_server(output_path: str = "iskala_openapi_server_enhanced.py") -> str:
    """
    Create enhanced server file with Graph Search integration
    
    Args:
        output_path: Where to save the enhanced server file
        
    Returns:
        Path to created file
    """
    handler = ToolServerIntegrationHandler()
    return handler.create_integrated_server_file(output_path)

# Export main components
__all__ = [
    "ToolServerIntegrationHandler",
    "quick_integrate_graph_search",
    "create_graph_enhanced_server"
] 