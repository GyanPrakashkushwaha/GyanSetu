
from models.schemas import ValidationScorecard, ExtractedKnowledge, PeriodContent, TeachingPeriod
import uuid
from core.prompts import Prompts
from infrastructure.llm_gateway import llm_gateway
from core.logger import app_logger
from typing import List
from core.exceptions import LLMGenerationError

class Validator:
    def __init__(self):
        pass
    
    def validation(self, metadata_json, teaching_periods: List[TeachingPeriod], period_contents: List[PeriodContent], job_id: str) -> ValidationScorecard:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        app_logger.info("Starting Stage 9: LLM-as-a-Judge Validation", extra={"extra_info": {"job_id": job_id, "stage": 9}})
        
        if not teaching_periods or not period_contents:
            app_logger.error("Missing data. Cannot validate without knowledge base and generated periods.")
            raise ValueError("Stage 9 Validation failed due to missing state data.")
        
        content_to_evaluate = ""
        source_truth = ""
        for i in range(len(teaching_periods)):
            content_to_evaluate += f"--- Period {period_contents[i].period_number}: {teaching_periods[i].focus_topic} ---\n{period_contents[i].script.main_body} \n\n"
            source_truth += f"{teaching_periods[i].concepts_covered} \n\n"
            
        
        # content_to_evaluate = "\n\n".join(
        #     [f"--- Period {p.period_number}: {p.focus_topic} ---\n{p.lesson_script}" for p in period_contents]
        # )
        
        messages = Prompts.Evaluation.LLM_AS_A_JUDGE_TEMPLATE.invoke({
            "metadata_json": metadata_json,
            "source_truth": source_truth,
            "generated_content": content_to_evaluate
        })
        
        try:
            scorecard: ValidationScorecard = llm_gateway.generate_structured(
                prompt=messages,
                response_model=ValidationScorecard,
                job_id=job_id
            )
            
            return scorecard
                
        except Exception as e:
            app_logger.error(f"Validation node failed: {str(e)}", extra={"extra_info": {"job_id": job_id}})
            raise LLMGenerationError(message="Stage 9 Failed", details={"job_id": job_id})

validator = Validator()