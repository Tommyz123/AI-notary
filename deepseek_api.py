<<<<<<< HEAD
import requests
from config import OPENAI_API_KEY  # 需要配置你的openai api key

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"

def call_openai(messages):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.4
    }

    response = requests.post(OPENAI_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenAI API 调用失败: {response.status_code} - {response.text}")
=======
import time, requests
from typing import List, Dict, Any
from config import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Reuse connections + auto-retry (429/5xx/connection reset/read timeout)
_SESSION = requests.Session()
retry = Retry(
    total=4,                # Total retry attempts
    read=4, connect=4, backoff_factor=0.7,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
_SESSION.mount("https://", HTTPAdapter(max_retries=retry))
_HEADERS = config.get_api_headers()



def call_deepseek(messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None) -> str:
    """
    Call DeepSeek API with enhanced error handling and security.
    
    Args:
        messages: List of message dictionaries for the conversation
        temperature: Override default temperature (optional)
        max_tokens: Override default max tokens (optional)
    
    Returns:
        AI response content
    
    Raises:
        Exception: If API call fails after retries
    """
    payload: Dict[str, Any] = {
        "model": config.DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature or config.DEFAULT_TEMPERATURE,
        "max_tokens": max_tokens or config.DEFAULT_MAX_TOKENS
    }

    def _post():
        # Set read timeout to 30s, connection timeout to 8s
        return _SESSION.post(config.DEEPSEEK_API_URL, json=payload, headers=_HEADERS, timeout=(8, 30))

    last_text = ""
    for attempt in range(4):  # Work with Retry for additional safety
        try:
            resp = _post()
            last_text = resp.text
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            # Non-retryable error: throw server response directly for easier debugging
            if resp.status_code not in (429, 500, 502, 503, 504):
                raise Exception(f"API call failed: {resp.status_code} - {last_text}")
        except (requests.ReadTimeout, requests.ConnectionError) as e:
            last_text = str(e)
        # Exponential backoff (stacks with urllib3 backoff for additional resilience)
        time.sleep(0.7 * (1.8 ** attempt))

    raise Exception(f"API call failed after multiple retries (timeout/failure) - {last_text}")

>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
