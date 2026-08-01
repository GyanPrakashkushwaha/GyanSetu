import logging
from langchain_openai import ChatOpenAI
from models.schemas import EducationalMetadata, ExtractedKnowledge
from infrastructure.llm_gateway import llm_gateway
from core.exceptions import ExtractionError
from core.prompts.Prompts import Extraction

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = 
        
        self.metadata_llm = self.llm.with_structured_output(EducationalMetadata)
        self.knowledge_llm = self.llm.with_structured_output(ExtractedKnowledge)

    def extract_metadata(self, raw_markdown: str) -> EducationalMetadata:
        logger.info("Starting Stage 2: Extracting Educational Metadata")
        
        chain = Extraction.EDUCATIONAL_METADATA_TEMPLATE | self.metadata_llm
        
        try:
            return chain.invoke({"text": raw_markdown})
        except Exception as e:
            logger.error(f"Stage 2 Failed: {str(e)}")
            raise ExtractionError(f"Failed to extract metadata: {str(e)}")

    def extract_knowledge(self, raw_markdown: str, metadata: EducationalMetadata) -> ExtractedKnowledge:
        """Stage 3: Structured Educational Representation"""
        logger.info("Starting Stage 3: Extracting Knowledge Base")
        
        chain = Extraction.KNOWLEDGE_EXTRACTION_TEMPLATE | self.knowledge_llm
        
        try:
            return chain.invoke({
                "text": raw_markdown,
                "grade": metadata.grade,
                "difficulty": metadata.difficulty,
                "subject": metadata.subject
            })
        except Exception as e:
            logger.error(f"Stage 3 Failed: {str(e)}")
            raise ExtractionError(f"Failed to extract knowledge base: {str(e)}")