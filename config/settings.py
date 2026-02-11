"""
Configuration management for Uncertainty-First Agent Council
"""
import os
from enum import Enum
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

class Settings:
    """Global configuration settings"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Council Settings
    ENABLE_INNER_COUNCIL: bool = os.getenv("ENABLE_INNER_COUNCIL", "false").lower() == "true"
    INNER_COUNCIL_SIZE: int = int(os.getenv("INNER_COUNCIL_SIZE", "3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        # Create logs directory
        self.LOGS_DIR.mkdir(exist_ok=True)
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate critical configuration"""
        if self.LLM_PROVIDER == LLMProvider.OPENAI and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        elif self.LLM_PROVIDER == LLMProvider.ANTHROPIC and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
        elif self.LLM_PROVIDER == LLMProvider.GEMINI and not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")

# Global settings instance
settings = Settings()
