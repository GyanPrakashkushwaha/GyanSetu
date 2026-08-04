
from sqlalchemy import select
from langchain_google_genai import ChatGoogleGenerativeAI
from infrastructure.vector_store import vector_store
from models.database import SessionLocal, DocumentChunk
from models.schemas import PeriodContent
from core.logger import app_logger
from core.config import GEMINI_API_KEY
from core.prompts import Prompts
from core.exceptions import LLMGenerationError
from infrastructure.llm_gateway import llm_gateway


class ContentGeneration:
    def __init__(self):
        pass
    def retrieve_relevant_chunks(self, job_id: str, query: str, limit: int = 3) -> str:
        query_vector = vector_store.embeddings.embed_query(query)
        with SessionLocal() as db:
            stmt = (
                select(DocumentChunk)
                .where(DocumentChunk.job_id == job_id)
                .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
                .limit(limit)
            )
            results = db.execute(stmt).scalars().all()
            
            context = ""
            for row in results:
                context += f"--- Source Section: {row.header_path} ---\n{row.content}\n\n"
                
            return context

    def generate_single_period(self, metadata, job_id: str, period) -> PeriodContent:
        app_logger.info(f"Generating content for Period: {period.focus_topic}")
        
        search_query = f"{period.focus_topic} {', '.join(period.concepts_covered)}"
        retrieved_context = self.retrieve_relevant_chunks(job_id, search_query)
        
        messages = Prompts.Generation.CLASSROOM_CONTENT_TEMPLATE.invoke({
            "metadata_json": metadata,
            "context": retrieved_context,
            "period_number": period.period_number,
            "focus_topic": period.focus_topic,
            "learning_outcome": period.learning_outcome,
            "concepts_covered": period.concepts_covered
        })
        
        try:
            result: PeriodContent = llm_gateway.generate_structured(
                prompt=messages,
                response_model=PeriodContent,
                job_id=job_id
            )
            app_logger.info(f"Successfully generated Period {result.period_number} Content!")
            return result
        except Exception as e:
            app_logger.error(f"Content generation failed for Period {period.period_number}: {str(e)}")
            raise LLMGenerationError(message=f"Failed to generate content for Period {period.period_number}: {str(e)}")

content_generator = ContentGeneration()