"""
Enhanced AI API module with multi-provider support and caching
Supports both OpenAI and DeepSeek APIs with intelligent caching for better performance.
"""

import time
import requests
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APICache:
    """Simple SQLite-based cache for API responses."""
    
    def __init__(self, db_path: str = "api_cache.db"):
        self.db_path = db_path
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize cache database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                cache_key TEXT PRIMARY KEY,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache (expires_at)
        """)
        conn.commit()
        conn.close()
    
    def _generate_cache_key(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> str:
        """Generate cache key from request parameters."""
        cache_data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Get cached response if available and not expired."""
        if not config.ENABLE_RESPONSE_CACHING:
            return None
        
        cache_key = self._generate_cache_key(messages, model, temperature, max_tokens)
        
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("""
            SELECT response FROM api_cache 
            WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
        """, (cache_key,)).fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def set(self, messages: List[Dict], model: str, temperature: float, max_tokens: int, response: str):
        """Cache the API response."""
        if not config.ENABLE_RESPONSE_CACHING:
            return
        
        cache_key = self._generate_cache_key(messages, model, temperature, max_tokens)
        expires_at = datetime.now() + timedelta(minutes=config.CACHE_DURATION_MINUTES)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO api_cache (cache_key, response, expires_at)
            VALUES (?, ?, ?)
        """, (cache_key, response, expires_at))
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM api_cache WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
        conn.close()


class AIAPIClient:
    """Enhanced AI API client with multi-provider support."""
    
    def __init__(self):
        self.cache = APICache()
        self._init_session()
    
    def _init_session(self):
        """Initialize HTTP session with retry strategy."""
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,  # Reduced for faster response
            read=3,
            connect=3,
            backoff_factor=0.5,  # Faster backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
    
    def _optimize_parameters_for_speed(self, temperature: float = None, max_tokens: int = None) -> tuple:
        """Optimize parameters for faster response while maintaining quality."""
        # For faster responses, we can slightly reduce max_tokens and adjust temperature
        optimized_temp = temperature if temperature is not None else config.DEFAULT_TEMPERATURE
        optimized_tokens = max_tokens if max_tokens is not None else min(config.DEFAULT_MAX_TOKENS, 600)
        
        # For OpenAI, we can use more aggressive optimization
        if config.API_PROVIDER == "openai":
            optimized_tokens = min(optimized_tokens, 500)  # OpenAI is faster with fewer tokens
        
        return optimized_temp, optimized_tokens
    
    def call_ai_api(self, messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None) -> str:
        """
        Call AI API with caching and multi-provider support.
        
        Args:
            messages: List of message dictionaries for the conversation
            temperature: Override default temperature (optional)
            max_tokens: Override default max tokens (optional)
        
        Returns:
            AI response content
        
        Raises:
            Exception: If API call fails after retries
        """
        # Optimize parameters for speed
        opt_temperature, opt_max_tokens = self._optimize_parameters_for_speed(temperature, max_tokens)
        
        # Check cache first
        cached_response = self.cache.get(messages, config.CURRENT_MODEL, opt_temperature, opt_max_tokens)
        if cached_response:
            return cached_response
        
        # Prepare API request
        payload = {
            "model": config.CURRENT_MODEL,
            "messages": messages,
            "temperature": opt_temperature,
            "max_tokens": opt_max_tokens
        }
        
        # Add provider-specific optimizations
        if config.API_PROVIDER == "openai":
            payload["stream"] = False  # Disable streaming for faster response
            # payload["top_p"] = 0.9  # Can add for more focused responses
        
        headers = config.get_api_headers()
        
        # Set optimized timeouts (shorter for faster responses)
        timeout = (5, 20) if config.API_PROVIDER == "openai" else (8, 30)
        
        last_error = ""
        for attempt in range(3):  # Reduced retry attempts for speed
            try:
                response = self.session.post(
                    config.CURRENT_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    
                    # Cache the successful response
                    self.cache.set(messages, config.CURRENT_MODEL, opt_temperature, opt_max_tokens, result)
                    
                    return result
                
                # Handle non-retryable errors
                if response.status_code not in (429, 500, 502, 503, 504):
                    raise Exception(f"API call failed: {response.status_code} - {response.text}")
                
                last_error = f"HTTP {response.status_code}: {response.text}"
                
            except (requests.ReadTimeout, requests.ConnectionError) as e:
                last_error = str(e)
            
            # Shorter backoff for faster retry
            if attempt < 2:
                time.sleep(0.5 * (1.5 ** attempt))
        
        raise Exception(f"API call failed after retries - {last_error}")
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get current API provider information."""
        return {
            "provider": config.API_PROVIDER,
            "model": config.CURRENT_MODEL,
            "api_url": config.CURRENT_API_URL,
            "caching_enabled": config.ENABLE_RESPONSE_CACHING
        }


# Global API client instance
ai_client = AIAPIClient()

# Backward compatibility function
def call_deepseek(messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None) -> str:
    """
    Backward compatibility function that now supports multiple providers.
    """
    return ai_client.call_ai_api(messages, temperature, max_tokens)


# Cleanup function for maintenance
def cleanup_cache():
    """Clean up expired cache entries."""
    ai_client.cache.cleanup_expired()


if __name__ == "__main__":
    # Test the API
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]
    
    print(f"Testing API with provider: {config.API_PROVIDER}")
    print(f"Model: {config.CURRENT_MODEL}")
    
    try:
        response = call_deepseek(test_messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")