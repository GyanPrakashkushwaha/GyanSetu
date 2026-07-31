import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.models.schemas import EducationalMetadata, ExtractedKnowledge
from app.core.exceptions import ExtractionError

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """
    Handles Stage 2 and Stage 3 of the pipeline.
    Transforms raw Markdown into validated Pydantic schemas.
    """
    def __init__(self, model_name: str = "gpt-4o"):
        # We use a low temperature for deterministic, factual extraction
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        
        # Bind our Pydantic schemas to the LLM to guarantee JSON structure
        self.metadata_llm = self.llm.with_structured_output(EducationalMetadata)
        self.knowledge_llm = self.llm.with_structured_output(ExtractedKnowledge)

    def extract_metadata(self, raw_markdown: str) -> EducationalMetadata:
        """Stage 2: Educational Classification"""
        logger.info("Starting Stage 2: Extracting Educational Metadata")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert curriculum designer. Analyze the following educational text and classify its domain, target audience, and difficulty level."),
            ("human", "{text}")
        ])
        
        chain = prompt | self.metadata_llm
        
        try:
            return chain.invoke({"text": raw_markdown})
        except Exception as e:
            logger.error(f"Stage 2 Failed: {str(e)}")
            raise ExtractionError(f"Failed to extract metadata: {str(e)}")

    def extract_knowledge(self, raw_markdown: str, metadata: EducationalMetadata) -> ExtractedKnowledge:
        """Stage 3: Structured Educational Representation"""
        logger.info("Starting Stage 3: Extracting Knowledge Base")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert teacher preparing a lesson plan. Extract the core educational components "
                "from the text. Keep the target audience in mind: {grade} students at a {difficulty} level "
                "studying {subject}."
            )),
            ("human", "{text}")
        ])
        
        chain = prompt | self.knowledge_llm
        
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