#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 ISKALA Secure Configuration Management
========================================

Centralized, secure configuration management для всех ISKALA сервисов.
Заменяет все hardcoded секреты на environment variables с валидацией.

Security Features:
- ✅ No hardcoded secrets  
- ✅ Environment-based configuration
- ✅ Validation и type checking
- ✅ Development/Production modes
- ✅ Sensitive data masking в logs
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator, SecretStr
from enum import Enum

class EnvironmentMode(str, Enum):
    """Environment modes for different deployment stages"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ISKALASecureConfig(BaseSettings):
    """
    🔐 Secure Configuration для всех ISKALA сервисов
    
    Все секреты загружаются из environment variables.
    Никаких hardcoded значений в коде!
    """
    
    # ================================
    # 🌍 Environment Configuration
    # ================================
    ENVIRONMENT: EnvironmentMode = Field(
        default=EnvironmentMode.DEVELOPMENT,
        description="Deployment environment"
    )
    
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (только для development)"
    )
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # ================================
    # 🔐 Authentication & Security  
    # ================================
    
    # OpenRouter API (КРИТИЧНО - НЕ hardcode!)
    OPENROUTER_API_KEY: SecretStr = Field(
        description="OpenRouter API key для LLM requests",
        min_length=10
    )
    
    OPENROUTER_MODEL: str = Field(
        default="moonshotai/kimi-k2",
        description="Default OpenRouter model"
    )
    
    # WebUI Secret Key (КРИТИЧНО - НЕ hardcode!)
    WEBUI_SECRET_KEY: SecretStr = Field(
        description="Secret key для WebUI sessions",
        min_length=32
    )
    
    # API Keys для Tool Server
    API_KEYS: List[str] = Field(
        default_factory=list,
        description="Valid API keys для Tool Server access"
    )
    
    ENABLE_API_KEY_AUTH: bool = Field(
        default=True,
        description="Enable API key authentication"
    )
    
    # ================================
    # 🗄️ Database Configuration
    # ================================
    
    # Neo4j Database (КРИТИЧНО - НЕ hardcode пароли!)
    NEO4J_URI: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI"
    )
    
    NEO4J_USERNAME: str = Field(
        default="neo4j",
        description="Neo4j username"
    )
    
    NEO4J_PASSWORD: SecretStr = Field(
        description="Neo4j password - ОБЯЗАТЕЛЬНО в .env",
        min_length=8
    )
    
    NEO4J_DATABASE: str = Field(
        default="iskala-mova",
        description="Neo4j database name"
    )
    
    # Redis Cache (КРИТИЧНО - НЕ hardcode пароли!)
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis host"
    )
    
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis port"
    )
    
    REDIS_PASSWORD: Optional[SecretStr] = Field(
        default=None,
        description="Redis password - рекомендуется в production"
    )
    
    REDIS_DB: int = Field(
        default=0,
        description="Redis database number"
    )
    
    # ================================
    # 🌐 Web Server Configuration
    # ================================
    
    # Service Ports
    ISKALA_PORT: int = Field(default=8001, description="ISKALA Core port")
    VAULT_PORT: int = Field(default=8081, description="Vault service port") 
    TRANSLATION_PORT: int = Field(default=8082, description="Translation service port")
    RAG_PORT: int = Field(default=8002, description="RAG service port")
    TOOL_SERVER_PORT: int = Field(default=8003, description="Tool Server port")
    GRAPH_SEARCH_PORT: int = Field(default=8004, description="Graph Search port")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins - НЕ использовать ['*'] в production!"
    )
    
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=False,
        description="Allow credentials в CORS - рекомендуется False"
    )
    
    # ================================
    # ⚡ Performance & Rate Limiting
    # ================================
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Requests per window для rate limiting"
    )
    
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Rate limit window в секундах"
    )
    
    # Performance Settings  
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=100,
        description="Maximum concurrent requests"
    )
    
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Request timeout в секундах"  
    )
    
    # ================================
    # 📊 Monitoring Configuration
    # ================================
    
    ENABLE_METRICS: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    
    METRICS_PORT: int = Field(
        default=9090,
        description="Metrics server port"
    )
    
    # ================================
    # 🔍 Validation Methods
    # ================================
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        """Ensure environment is valid"""
        if isinstance(v, str):
            v = EnvironmentMode(v.lower())
        return v
    
    @validator('OPENROUTER_API_KEY')
    def validate_openrouter_key(cls, v):
        """Validate OpenRouter API key format"""
        if isinstance(v, SecretStr):
            key = v.get_secret_value()
        else:
            key = str(v)
            
        if not key.startswith('sk-or-v1-'):
            raise ValueError('OpenRouter API key должен начинаться с sk-or-v1-')
        return v
    
    @validator('API_KEYS', pre=True)
    def parse_api_keys(cls, v):
        """Parse comma-separated API keys"""
        if isinstance(v, str):
            return [key.strip() for key in v.split(',') if key.strip()]
        return v
    
    @validator('ALLOWED_ORIGINS', pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @validator('DEBUG')
    def debug_only_in_development(cls, v, values):
        """Debug mode только в development"""
        if v and values.get('ENVIRONMENT') == EnvironmentMode.PRODUCTION:
            raise ValueError('DEBUG не может быть True в production environment')
        return v
    
    # ================================
    # 🛡️ Security Methods
    # ================================
    
    def get_database_url(self) -> str:
        """Get complete database URL with credentials"""
        password = self.NEO4J_PASSWORD.get_secret_value()
        return f"neo4j://{self.NEO4J_USERNAME}:{password}@{self.NEO4J_URI.replace('bolt://', '')}"
    
    def get_redis_url(self) -> str:
        """Get Redis URL with optional password"""
        if self.REDIS_PASSWORD:
            password = self.REDIS_PASSWORD.get_secret_value()
            return f"redis://:{password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == EnvironmentMode.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == EnvironmentMode.DEVELOPMENT
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get secure CORS configuration"""
        if self.is_development():
            return {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"]
            }
        else:
            return {
                "allow_origins": self.ALLOWED_ORIGINS,
                "allow_credentials": self.CORS_ALLOW_CREDENTIALS,  
                "allow_methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "X-API-Key", "Authorization"]
            }
    
    def mask_sensitive_data(self) -> Dict[str, Any]:
        """Get config dict with masked sensitive data для logging"""
        config_dict = self.dict()
        
        # Mask sensitive fields
        sensitive_fields = [
            'OPENROUTER_API_KEY', 'WEBUI_SECRET_KEY', 
            'NEO4J_PASSWORD', 'REDIS_PASSWORD', 'API_KEYS'
        ]
        
        for field in sensitive_fields:
            if field in config_dict and config_dict[field] is not None:
                if isinstance(config_dict[field], list):
                    config_dict[field] = ['***MASKED***'] * len(config_dict[field])
                else:
                    config_dict[field] = '***MASKED***'
        
        return config_dict
    
    # ================================
    # ⚙️ Configuration Loading
    # ================================
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
        validate_assignment = True
        
        # Security: don't expose secrets in repr
        repr_include_secrets = False

# ================================
# 🌍 Global Configuration Instance
# ================================

def load_config() -> ISKALASecureConfig:
    """
    Load configuration with validation
    
    Raises:
        ValidationError: If configuration is invalid
        FileNotFoundError: If required .env file missing in production
    """
    try:
        config = ISKALASecureConfig()
        
        # Additional production validation
        if config.is_production():
            _validate_production_config(config)
        
        return config
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        print(f"💡 Ensure .env file exists with all required variables")
        print(f"📋 See .env.template for required variables")
        raise

def _validate_production_config(config: ISKALASecureConfig):
    """Additional validation for production environment"""
    
    # Check critical secrets are not default values
    openrouter_key = config.OPENROUTER_API_KEY.get_secret_value()
    webui_secret = config.WEBUI_SECRET_KEY.get_secret_value()
    neo4j_password = config.NEO4J_PASSWORD.get_secret_value()
    
    if 'change_this' in openrouter_key.lower():
        raise ValueError("OPENROUTER_API_KEY still has default value in production")
    
    if 'change_this' in webui_secret.lower() or webui_secret == 'iskala-secret-key-2024':
        raise ValueError("WEBUI_SECRET_KEY still has default value in production")
        
    if 'change_this' in neo4j_password.lower():
        raise ValueError("NEO4J_PASSWORD still has default value in production")
    
    # Ensure secure CORS in production
    if "*" in config.ALLOWED_ORIGINS:
        raise ValueError("ALLOWED_ORIGINS cannot contain '*' in production")

# Global config instance
try:
    config = load_config()
    print(f"✅ ISKALA Configuration loaded successfully")
    print(f"🌍 Environment: {config.ENVIRONMENT.value}")
    print(f"🔧 Debug mode: {config.DEBUG}")
except Exception as e:
    print(f"❌ CRITICAL: Configuration failed to load: {e}")
    config = None

__all__ = ['ISKALASecureConfig', 'load_config', 'config', 'EnvironmentMode'] 