import uuid
from core.logger import app_logger
from models.schemas import EducationalMetadata, ExtractedKnowledge
from infrastructure.llm_gateway import llm_gateway
from core.exceptions import ExtractionError
from core.prompts import Prompts

class KnowledgeExtractor:
    def __init__(self):
        pass

    def extract_metadata(self, raw_markdown: str, job_id: str = None) -> EducationalMetadata:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        
        app_logger.info(
            "Starting Stage 2: Extracting Educational Metadata",
            extra={"extra_info": {"job_id": job_id}}
        )
        
        messages = Prompts.Extraction.EDUCATIONAL_METADATA_TEMPLATE.invoke({
            "text_content": raw_markdown
        })
        
        try:
            return llm_gateway.generate_structured(
                prompt=messages,
                response_model=EducationalMetadata,
                job_id=job_id
            )
        except Exception as e:
            app_logger.error(
                f"Stage 2 Failed: {str(e)}",
                extra={"extra_info": {"job_id": job_id}}
            )
            raise ExtractionError(f"Failed to extract metadata: {str(e)}")

    def extract_knowledge(self, raw_markdown: str, metadata: EducationalMetadata, job_id: str = None) -> ExtractedKnowledge:
        job_id = job_id or f"know_{uuid.uuid4().hex[:8]}"
        
        app_logger.info(
            "Starting Stage 3: Extracting Knowledge Base",
            extra={"extra_info": {"job_id": job_id}}
        )
        
        messages = Prompts.Extraction.KNOWLEDGE_EXTRACTION_TEMPLATE.invoke({
            "text": raw_markdown,
            "grade": metadata.grade,
            "difficulty": metadata.difficulty,
            "subject": metadata.subject
        })
        
        try:
            return llm_gateway.generate_structured(
                prompt=messages,
                response_model=ExtractedKnowledge,
                job_id=job_id
            )
        except Exception as e:
            app_logger.error(
                f"Stage 3 Failed: {str(e)}",
                extra={"extra_info": {"job_id": job_id}}
            )
            raise ExtractionError(f"Failed to extract knowledge base: {str(e)}")
        
knowledge_extractor = KnowledgeExtractor()