
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
        generated_content_map = {p.period_number: p for p in period_contents}

        for planned_period in teaching_periods:
            generated_period = generated_content_map.get(planned_period.period_number)
            
            if not generated_period:
                app_logger.error(f"Missing generated content for Period {planned_period.period_number}")
                continue 
            script_text = "\n".join(generated_period.script.main_body)
            
            content_to_evaluate += f"--- Period {planned_period.period_number}: {planned_period.focus_topic} ---\n{script_text}\n\n"
            source_truth += f"--- Period {planned_period.period_number} Truth ---\n{planned_period.concepts_covered}\n\n"
            
        
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