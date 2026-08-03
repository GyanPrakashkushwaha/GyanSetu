from core.logger import app_logger
from core.exceptions import LLMGenerationError
from models.schemas import LearningGapAnalysis
from infrastructure.llm_gateway import llm_gateway
from models.schemas import ExtractedKnowledge
from core.prompts import Prompts
import uuid

class LearningGapAnalyzer:
    def __init__(self):
        pass

    def learning_gap_node(self, metadata_json, job_id: str, knowledge_base: ExtractedKnowledge) -> dict:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        app_logger.info(f"Starting Stage 8: Learning Gap Analysis for job {job_id}")

        if not knowledge_base:
            raise ValueError("Knowledge base missing from state. Cannot perform Stage 8.")

        misconceptions = knowledge_base.misconceptions
        concepts = knowledge_base.concepts

        if not misconceptions:
            app_logger.info("No misconceptions found in Stage 3. Returning empty gap analysis.")
            return {"learning_gaps": LearningGapAnalysis(gaps=[])}

        messages = Prompts.Generation.LEARNING_GAP_TEMPLATE.invoke({
            "metadata_json": metadata_json,
            "concepts": ", ".join(concepts),
            "misconceptions": "\n- ".join(misconceptions)
        })

        try:
            result: LearningGapAnalysis = llm_gateway.generate_structured(
                prompt=messages,
                response_model=LearningGapAnalysis,
                job_id=job_id
            )
            
            app_logger.info(f"Successfully identified {len(result.gaps)} learning gaps!")
            
            return result
            
        except Exception as e:
            app_logger.error(f"Learning Gap Analysis failed: {str(e)}")
            raise LLMGenerationError(message=f"Failed to generate learning gaps: {str(e)}")
        
learning_gap_analyzer = LearningGapAnalyzer()