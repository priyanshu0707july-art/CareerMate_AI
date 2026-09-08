import json
import logging
from abc import ABC, abstractmethod
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from app.config import settings

logger = logging.getLogger(__name__)

class LLMException(Exception):
    """Base exception for LLM failures"""
    pass

class LLMRateLimitException(LLMException):
    """Raised when LLM API rate limit is exceeded"""
    pass

class LLMTimeoutException(LLMException):
    """Raised when LLM API times out"""
    pass

class LLMInvalidJSONException(LLMException):
    """Raised when LLM returns malformed JSON"""
    pass

class BaseLLMProvider(ABC):
    """Abstract base class for LLM Providers"""
    
    @abstractmethod
    def generate_json(self, prompt: str) -> dict:
        """
        Takes a prompt string and returns a parsed JSON dictionary.
        Must handle its own API-specific exceptions and wrap them in LLMException.
        """
        pass

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_json(self, prompt: str) -> dict:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                ),
            )
            
            if not response.text:
                raise LLMException("Empty response received from Gemini API")
                
            return json.loads(response.text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received from Gemini API: {e}")
            raise LLMInvalidJSONException("The AI returned malformed JSON.") from e
        except GoogleAPIError as e:
            # Simplistic error categorization
            error_str = str(e).lower()
            if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                logger.error(f"Gemini API Rate Limit hit: {e}")
                raise LLMRateLimitException("AI provider rate limit exceeded.") from e
            if "timeout" in error_str or "deadline" in error_str or "504" in error_str:
                logger.error(f"Gemini API Timeout: {e}")
                raise LLMTimeoutException("AI provider timed out.") from e
            
            logger.error(f"Gemini API failed: {e}")
            raise LLMException(f"AI Provider failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in GeminiLLMProvider: {e}")
            raise LLMException(f"An unexpected error occurred during AI generation: {str(e)}") from e

# Singleton instance
llm_provider = GeminiLLMProvider()
