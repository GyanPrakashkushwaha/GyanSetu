
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type
)
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from openai import RateLimitError, APIConnectionError

from core.logger import app_logger
from core.exceptions import LLMGenerationError
from core.config import OPENAI_API_KEY, GEMINI_API_KEY
# Type variable for Pydantic schemas
T = TypeVar('T', bound=BaseModel)

class LLMGateway:
    """
    Centralized Gateway for all LLM interactions. 
    Enforces retry logic, logging, and dependency inversion.
    """
    MAX_RETRIES = 5
    def __init__(self):
        self.model_name = "gpt-4o-mini"
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        # self.model_name = "models/gemini-3.5-flash"
        # self.llm = GoogleGenerativeAI(
        #     model=self.model_name,
        #     temperature=0.2,
        #     api_key=GEMINI_API_KEY
        # )

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential_jitter(initial=1, max=60, exp_base=2, jitter=1),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        reraise=True
    )
    def generate(self, prompt: Any, job_id: str) -> str:
        """
        Executes a standard LLM call returning raw text.
        Accepts a string, a list of messages, or a formatted ChatPromptValue.
        """
        app_logger.info(
            "Sending standard request to LLM Gateway", 
            extra={"extra_info": {"job_id": job_id, "model": self.model_name}}
        )
        
        try:
            result = self.llm.invoke(prompt)
            
            # return result
            return result.content # REPLACE TO THIS WHEN SWICHING TO OPENAI MODEL.
            
        except RateLimitError as e:
            app_logger.warning(f"Rate limit hit, triggering backoff...", extra={"extra_info": {"job_id": job_id}})
            raise e 
            
        except Exception as e:
            app_logger.error(f"Fatal LLM Error: {str(e)}", extra={"extra_info": {"job_id": job_id}})
            raise LLMGenerationError(
                message="Failed to generate standard text from LLM", 
                details={"error": str(e), "job_id": job_id}
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
            raise e 
            
        except Exception as e:
            app_logger.error(f"Fatal LLM Error: {str(e)}", extra={"extra_info": {"job_id": job_id}})
            raise LLMGenerationError(
                message="Failed to generate structured data from LLM", 
                details={"error": str(e), "job_id": job_id}
            )

llm_gateway = LLMGateway()