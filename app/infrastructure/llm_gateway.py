
import os
from typing import Type, TypeVar
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type
)
from langchain_openai import ChatOpenAI
from openai import RateLimitError, APIConnectionError

from app.core.logger import app_logger
from app.core.exceptions import LLMGenerationError

# Type variable for Pydantic schemas
T = TypeVar('T', bound=BaseModel)

class LLMGateway:
    """
    Centralized Gateway for all LLM interactions. 
    Enforces retry logic, logging, and dependency inversion.
    """
    def __init__(self):
        self.model_name = "gpt-4o"
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.MAX_RETRIES = 5

    # Tenacity Decorator: Max 5 retries, exponential backoff starting at 1s up to 60s, with jitter.
    @retry(
        stop=stop_after_attempt(self.MAX_RETRIES),
        wait=wait_exponential_jitter(initial=1, max=60, exp_base=2, jitter=1),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        reraise=True
    )
    def generate_structured(self, prompt: str, response_model: Type[T], job_id: str) -> T:
        """
        Executes an LLM call forcing a structured Pydantic output.
        """
        app_logger.info(
            "Sending request to LLM Gateway", 
            extra={"extra_info": {"job_id": job_id, "model": self.model_name}}
        )
        
        try:
            structured_llm = self.llm.with_structured_output(response_model)
            result = structured_llm.invoke(prompt)
            return result
            
        except RateLimitError as e:
            app_logger.warning(f"Rate limit hit, triggering backoff...", extra={"extra_info": {"job_id": job_id}})
            raise e # Let Tenacity catch it and retry
            
        except Exception as e:
            # For non-retryable errors (like prompt too large, or Pydantic validation failure)
            app_logger.error(f"Fatal LLM Error: {str(e)}", extra={"extra_info": {"job_id": job_id}})
            raise LLMGenerationError(
                message="Failed to generate structured data from LLM", 
                details={"error": str(e), "job_id": job_id}
            )

llm_gateway = LLMGateway()