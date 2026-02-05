"""
Configuration
Manages system configuration and environment variables.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    System configuration manager.
    Loads from environment variables with sensible defaults.
    """
    
    def __init__(self):
        # API Keys
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        
        # Model Configuration
        self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
        
        # Agent Configuration
        self.MAX_HEAL_ATTEMPTS = int(os.getenv("MAX_HEAL_ATTEMPTS", "5"))
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        
        # Output Configuration
        self.OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Feature Flags
        self.ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
        self.ENABLE_DEPLOYMENT = os.getenv("ENABLE_DEPLOYMENT", "false").lower() == "true"
        
        # Cloud Configuration
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        self.AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
        
        # Database Configuration (for generated apps)
        self.DEFAULT_DB_TYPE = os.getenv("DEFAULT_DB_TYPE", "postgresql")
        
        # Performance
        self.PARALLEL_AGENTS = os.getenv("PARALLEL_AGENTS", "false").lower() == "true"
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # Validation
        self._validate()
    
    def _validate(self):
        """Validate critical configuration"""
        if not self.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Set it with: export ANTHROPIC_API_KEY='your-api-key'"
            )
    
    def get_agent_config(self, agent_name: str) -> dict:
        """Get configuration specific to an agent"""
        base_config = {
            "model": self.CLAUDE_MODEL,
            "max_tokens": self.MAX_TOKENS,
            "api_key": self.ANTHROPIC_API_KEY
        }
        
        # Agent-specific overrides
        if agent_name == "healer":
            base_config["max_attempts"] = self.MAX_HEAL_ATTEMPTS
        
        return base_config
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return {
            "claude_model": self.CLAUDE_MODEL,
            "max_tokens": self.MAX_TOKENS,
            "max_heal_attempts": self.MAX_HEAL_ATTEMPTS,
            "max_retry_attempts": self.MAX_RETRY_ATTEMPTS,
            "output_dir": str(self.OUTPUT_DIR),
            "log_level": self.LOG_LEVEL,
            "enable_web_search": self.ENABLE_WEB_SEARCH,
            "enable_deployment": self.ENABLE_DEPLOYMENT,
            "aws_region": self.AWS_REGION,
            "default_db_type": self.DEFAULT_DB_TYPE,
            "parallel_agents": self.PARALLEL_AGENTS,
            "cache_enabled": self.CACHE_ENABLED
        }
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'Config':
        """Load configuration from a file"""
        # TODO: Implement file-based config loading
        return cls()
    
    def __repr__(self) -> str:
        config_dict = self.to_dict()
        config_dict["api_key"] = "***hidden***"  # Don't expose API key
        return f"Config({config_dict})"


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    
    def __init__(self):
        super().__init__()
        self.LOG_LEVEL = "DEBUG"
        self.MAX_HEAL_ATTEMPTS = 3  # Fewer attempts in dev


class ProductionConfig(Config):
    """Production-specific configuration"""
    
    def __init__(self):
        super().__init__()
        self.LOG_LEVEL = "WARNING"
        self.MAX_HEAL_ATTEMPTS = 5


def get_config(environment: Optional[str] = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        environment: 'development', 'production', or None (uses env var)
    """
    if environment is None:
        environment = os.getenv("SDLC_ENV", "development")
    
    if environment == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()
