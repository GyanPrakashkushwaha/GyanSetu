import uuid
from core.logger import app_logger
from models.schemas import TeachingPlan, ExtractedKnowledge
from infrastructure.llm_gateway import llm_gateway
from core.exceptions import TeachingPlanError
from core.prompts import Prompts


class TeachingPlanner:
    def __init__(self):
        pass
    
    def planner(self, metadata_json, extracted_knowledge: ExtractedKnowledge, job_id: str = None) -> TeachingPlan:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        
        app_logger.info(
            "Starting Stage 4: Planning Teaching Content",
            extra={"extra_info": {"job_id": job_id}}
        )
        
        messages = Prompts.Planning.TEACHING_PLANNER_TEMPLATE.invoke({
            "metadata_json": metadata_json,
            "prerequisites": extracted_knowledge.prerequisites,
            "learning_objectives": extracted_knowledge.learning_objectives,
            "concepts": extracted_knowledge.concepts,
            "key_terms": extracted_knowledge.key_terms,
            "formulae": extracted_knowledge.formulae,
            "misconceptions": extracted_knowledge.misconceptions
        })
        
        try:
            return llm_gateway.generate_structured(
                prompt=messages,
                response_model=TeachingPlan,
                job_id=job_id
            )
        except Exception as e:
            app_logger.error(
                f"Stage 4 Failed: {str(e)}",
                extra={"extra_info": {"job_id": job_id}}
            )
            raise TeachingPlanError(f"Failed to plan teaching content: {str(e)}")
        
teaching_planner = TeachingPlanner()