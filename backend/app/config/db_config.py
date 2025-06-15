import os
from typing import Optional, Dict, Any
from functools import lru_cache

class DatabaseConfig:
    """Database configuration manager that handles both development and production environments."""
    
    def __init__(self):
        self._env = os.getenv('FLASK_ENV', 'development')
        self._is_production = self._env == 'production'
        
    @property
    def is_production(self) -> bool:
        return self._is_production
    
    @property
    def region_name(self) -> str:
        return os.getenv('AWS_REGION', 'us-east-1')
    
    @property
    def aws_access_key_id(self) -> Optional[str]:
        if self._is_production:
            # In production, these should be set via GitHub Actions secrets
            return os.getenv('AWS_ACCESS_KEY_ID')
        return os.getenv('DEV_AWS_ACCESS_KEY_ID', 'dummy-access-key')
    
    @property
    def aws_secret_access_key(self) -> Optional[str]:
        if self._is_production:
            return os.getenv('AWS_SECRET_ACCESS_KEY')
        return os.getenv('DEV_AWS_SECRET_ACCESS_KEY', 'dummy-secret-key')
    
    @property
    def endpoint_url(self) -> Optional[str]:
        """Returns DynamoDB endpoint URL. In production, this will be None (using AWS)."""
        if not self._is_production:
            return os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000')
        return None

@lru_cache()
def get_db_config() -> DatabaseConfig:
    """Returns a cached instance of DatabaseConfig."""
    return DatabaseConfig() 