"""Ollama client for local LLM interaction.

Handles communication with local Ollama API for AI responses.
Includes retry logic, timeout handling, and error recovery.
"""

import requests
import time
from core.logger import get_logger
from core.config import config

logger = get_logger("Ollama")


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self):
        self.host = config.get("ollama_host", "http://localhost:11434")
        self.model = config.get("ollama_model", "llama3")
        self.timeout = config.get("ollama_timeout", 60)
        self.retries = config.get("ollama_retries", 1)
    
    def is_available(self):
        """Check if Ollama service is running."""
        # Try a few quick attempts to detect the service (helps when the daemon is still starting)
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                response = requests.get(f"{self.host}/api/tags", timeout=5)
                if response.status_code == 200:
                    return True
                logger.debug(f"Ollama availability check returned {response.status_code}")
            except Exception as e:
                logger.debug(f"Ollama availability attempt {attempt} failed: {e}")
            # Backoff briefly between attempts
            time.sleep(0.5 * attempt)

        logger.error("Ollama availability check failed after retries")
        return False
    
    def list_models(self):
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(self, prompt, system_prompt=None, stream=False):
        """
        Generate response from Ollama.
        
        Args:
            prompt (str): User prompt
            system_prompt (str): Optional system prompt
            stream (bool): Whether to stream response
            
        Returns:
            str: Generated response or error message
        """
        # Handle model name variants (ensure :latest tag)
        model_name = self.model
        if not model_name.endswith(':latest'):
            model_name = f"{model_name}:latest"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        attempt = 0
        while attempt <= self.retries:
            attempt += 1
            
            try:
                if attempt > 1:
                    wait_time = 2 ** (attempt - 1)
                    logger.info(f"Retrying request (attempt {attempt}/{self.retries + 1}) after {wait_time}s")
                    time.sleep(wait_time)
                
                logger.debug(f"Sending request to Ollama (attempt {attempt})")
                
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('response', '').strip()
                    
                    if answer:
                        logger.debug(f"Received response ({len(answer)} chars)")
                        return answer
                    else:
                        logger.warning("Empty response from Ollama")
                        return "Sorry, I received an empty response."
                
                else:
                    logger.error(f"Ollama returned status code: {response.status_code}")
                    # 500 error likely means model is loading or busy - retry
                    if response.status_code == 500:
                        logger.warning("Ollama returned 500 (model loading?) - will retry...")
                        if attempt <= self.retries:
                            continue  # Retry
                    if attempt > self.retries:
                        return f"Sorry, AI service returned error code {response.status_code}."
                    
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out (attempt {attempt})")
                if attempt > self.retries:
                    return "Sorry, the AI request timed out."
                    
            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to Ollama service")
                return "Sorry, I couldn't connect to the AI service. Make sure Ollama is running."
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return f"Sorry, an unexpected error occurred: {str(e)}"
        
        return "Sorry, I couldn't get a response after multiple attempts."
    
    def warm_up(self):
        """Warm up the model with a simple request."""
        logger.info("Warming up Ollama model...")

        if not self.is_available():
            logger.warning("Cannot warm up: Ollama service is not available")
            return False

        # Attempt a single generate to warm model; handle failure gracefully
        try:
            result = self.generate("hello", stream=False)
            # If generate returns an error message string, treat as warm-up failure
            if isinstance(result, str) and result.lower().startswith("sorry"):
                logger.warning(f"Warm-up attempt returned an error: {result}")
                return False

            logger.info("Ollama warm-up complete")
            return True

        except Exception as e:
            logger.warning(f"Warm-up failed with exception: {e}")
            return False


# Global client instance
ollama_client = OllamaClient()


def ask_ai(prompt, verbose=True):
    """
    Legacy function for backward compatibility.
    
    Args:
        prompt (str): User prompt
        verbose (bool): Enable verbose logging
        
    Returns:
        str: AI response
    """
    return ollama_client.generate(prompt)
