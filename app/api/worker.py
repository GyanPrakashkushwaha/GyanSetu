
from .celery_app import celery_app
from pipelines.orchestrator import build_tkp_pipeline, PipelineState
from core.logger import app_logger
import psycopg_pool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from core.config import DB_CONNECTION_STRING 
from pipelines.phase1_extraction.parser import DocumentParser
from pathlib import Path
import json

safe_schemas = {
    ('models.schemas', 'EducationalMetadata'),
    ('models.schemas', 'SeverityLevel'),
    ('models.schemas', 'LearningGapAnalysis'),
    ('models.schemas', 'TeachingPlan'),
    ('models.schemas', 'ExtractedKnowledge'),
    ('models.schemas', 'PeriodContent')
}
custom_serializer = JsonPlusSerializer(allowed_msgpack_modules=safe_schemas)

def safe_serialize(model):
    if not model: return None
    return model.model_dump() if hasattr(model, 'model_dump') else model.dict()

# bind=True gives us access to 'self', allowing us to update the task state
@celery_app.task(bind=True, name="generate_tkp_task")
def run_background_pipeline(self, job_id: str, file_path: str, human_feedback: str = None):
    app_logger.info(f"Worker picked up job {job_id}")
    
    with psycopg_pool.ConnectionPool(conninfo=DB_CONNECTION_STRING, kwargs={"autocommit": True}) as pool:
        
        doc_parser = DocumentParser()
        raw_text = doc_parser.parse_document(Path(file_path))        
        checkpointer = PostgresSaver(pool, serde=custom_serializer)
        checkpointer.setup()
        workflow = build_tkp_pipeline(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": job_id}}
        
        if human_feedback:
            app_logger.info(f"Injecting human feedback for job {job_id}")
            workflow.update_state(
                config, 
                {"human_feedback": human_feedback}, 
                as_node="human_intervention" 
            )
            # We don't need initial_state when resuming, LangGraph pulls it from Postgres
            initial_state = None
        else:
            initial_state = PipelineState(
                job_id=job_id,
                raw_text=raw_text,
                metadata=None,
                knowledge_base=None,
                validation_errors=[],
                current_stage="Initialized"
            )

        try:
            for event in workflow.stream(initial_state, config=config):
                for node_name, state_update in event.items():
                    current_stage = state_update.get("current_stage", node_name)
                    current_stage_data = workflow.get_state(config).values
                    
                    tkp_current_data = {
                        "metadata": safe_serialize(current_stage_data.get("metadata", None)),
                        "knowledge_base": safe_serialize(current_stage_data.get("knowledge_base", None)),
                        "teaching_plan": safe_serialize(current_stage_data.get("teaching_plan", None)),
                        "learning_gaps": safe_serialize(current_stage_data.get("learning_gaps", None)),
                        "period_contents": [safe_serialize(p) for p in current_stage_data.get("period_contents", [])]
                    }
                    
                    self.update_state(
                        state="IN_PROGRESS", 
                        meta={"stage": current_stage, "node": node_name, "data": tkp_current_data}
                    )
                    app_logger.info(f"Job {job_id} transitioned to {node_name}")
                    
            final_state = workflow.get_state(config).values

            tkp_data = {
                "metadata": safe_serialize(final_state.get("metadata")),
                "knowledge_base": safe_serialize(final_state.get("knowledge_base")),
                "teaching_plan": safe_serialize(final_state.get("teaching_plan")),
                "learning_gaps": safe_serialize(final_state.get("learning_gaps")),
                "period_contents": [safe_serialize(p) for p in final_state.get("period_contents", [])]
            }
            with open(f"../samples/TeacherKnowledgePackage{job_id}.json", "w") as f:
                json.dump(tkp_data, f, indent=4)
                
            return {"stage": "Complete", "status": "SUCCESS", "data": tkp_data}
        
        except Exception as e:
            app_logger.error(f"Pipeline failed for {job_id}: {str(e)}")
            self.update_state(state="FAILED", meta={"error": str(e), "stage": "Failed"})
            raise e