# config.py
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class that loads settings from environment variables."""
    
    def __init__(self):
        self._validate_required_env_vars()
    
    @property
    def API_PROVIDER(self) -> str:
        """Current API provider (openai or deepseek)."""
        return os.getenv("API_PROVIDER", "openai").lower()
    
    @property
    def OPENAI_API_KEY(self) -> str:
        """OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def OPENAI_API_URL(self) -> str:
        """OpenAI API URL from environment variables."""
        return os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    
    @property
    def OPENAI_MODEL(self) -> str:
        """OpenAI model name from environment variables."""
        return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        """DeepSeek API key from environment variables."""
        return os.getenv("DEEPSEEK_API_KEY", "")
    
    @property
    def DEEPSEEK_API_URL(self) -> str:
        """DeepSeek API URL from environment variables."""
        return os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    
    @property
    def DEEPSEEK_MODEL(self) -> str:
        """DeepSeek model name from environment variables."""
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    @property
    def CURRENT_API_KEY(self) -> str:
        """Get API key for current provider."""
        if self.API_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        else:
            return self.DEEPSEEK_API_KEY
    
    @property
    def CURRENT_API_URL(self) -> str:
        """Get API URL for current provider."""
        if self.API_PROVIDER == "openai":
            return self.OPENAI_API_URL
        else:
            return self.DEEPSEEK_API_URL
    
    @property
    def CURRENT_MODEL(self) -> str:
        """Get model name for current provider."""
        if self.API_PROVIDER == "openai":
            return self.OPENAI_MODEL
        else:
            return self.DEEPSEEK_MODEL
    
    @property
    def APP_NAME(self) -> str:
        """Application name."""
        return os.getenv("APP_NAME", "Notary Training System")
    
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Maximum content length for processing."""
        return int(os.getenv("MAX_CONTENT_LENGTH", "12000"))
    
    @property
    def DEFAULT_TEMPERATURE(self) -> float:
        """Default temperature for AI responses."""
        return float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
    
    @property
    def DEFAULT_MAX_TOKENS(self) -> int:
        """Default max tokens for AI responses."""
        return int(os.getenv("DEFAULT_MAX_TOKENS", "800"))
    
    @property
    def RATE_LIMIT_PER_MINUTE(self) -> int:
        """Rate limit per minute for API calls."""
        return int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    
    @property
    def SESSION_TIMEOUT_MINUTES(self) -> int:
        """Session timeout in minutes."""
        return int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    
    @property
    def ENABLE_RESPONSE_CACHING(self) -> bool:
        """Enable response caching for better performance."""
        return os.getenv("ENABLE_RESPONSE_CACHING", "true").lower() == "true"
    
    @property
    def CACHE_DURATION_MINUTES(self) -> int:
        """Cache duration in minutes."""
        return int(os.getenv("CACHE_DURATION_MINUTES", "60"))
    
    def _validate_required_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        api_provider = self.API_PROVIDER
        
        if api_provider == "openai":
            required_key = "OPENAI_API_KEY"
        else:
            required_key = "DEEPSEEK_API_KEY"
        
        if not os.getenv(required_key):
            print(f"❌ Missing required API key: {required_key}")
            print(f"Current API provider: {api_provider}")
            print("Please check your .env file or environment configuration.")
            sys.exit(1)
    
    def get_api_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.CURRENT_API_KEY}",
            "Content-Type": "application/json"
        }

# Create global config instance
config = Config()

# Backward compatibility - expose old variable names
OPENAI_API_KEY = config.CURRENT_API_KEY
OPENAI_API_URL = config.CURRENT_API_URL  
OPENAI_MODEL = config.CURRENT_MODEL
