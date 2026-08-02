import uuid
from core.logger import app_logger
from models.schemas import KeyTerm, TeachingPlan
from infrastructure.llm_gateway import llm_gateway
from core.exceptions import TeachingPlanError
from core.prompts import Prompts
from typing import List


class TeachingPlanner:
    def __init__(self):
        pass
    
    def planner(self, metadata_json, prerequisites: List[str], learning_objectives: List[str], concepts: List[str], key_terms: List[KeyTerm], formulae: List[str], misconceptions: List[str], job_id: str = None) -> TeachingPlan:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        
        app_logger.info(
            "Starting Stage 3: Planning Teaching Content",
            extra={"extra_info": {"job_id": job_id}}
        )
        
        messages = Prompts.Planning.TEACHING_PLANNER_TEMPLATE.invoke({
            "metadata_json": metadata_json,
            "prerequisites": prerequisites,
            "learning_objectives": learning_objectives,
            "concepts": concepts,
            "key_terms": key_terms,
            "formulae": formulae,
            "misconceptions": misconceptions
        })
        
        try:
            return llm_gateway.generate_structured(
                prompt=messages,
                response_model=TeachingPlan,
                job_id=job_id
            )
        except Exception as e:
            app_logger.error(
                f"Stage 3 Failed: {str(e)}",
                extra={"extra_info": {"job_id": job_id}}
            )
            raise TeachingPlanError(f"Failed to plan teaching content: {str(e)}")
        
teaching_planner = TeachingPlanner()