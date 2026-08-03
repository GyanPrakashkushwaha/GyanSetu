
from .celery_app import celery_app
from pipelines.orchestrator import build_tkp_pipeline, PipelineState
from core.logger import app_logger

# bind=True gives us access to 'self', allowing us to update the task state
@celery_app.task(bind=True, name="generate_tkp_task")
def run_background_pipeline(self, job_id: str, text: str):
    app_logger.info(f"Worker picked up job {job_id}")
    
    checkpointer = None 
    workflow = build_tkp_pipeline(checkpointer)
    config = {"configurable": {"thread_id": job_id}}
    
    initial_state = PipelineState(
        job_id=job_id,
        raw_text=text,
        metadata=None,
        knowledge_base=None,
        validation_errors=[],
        current_stage="Initialized"
    )

    try:
        for event in workflow.stream(initial_state, config=config):
            for node_name, state_update in event.items():
                current_stage = state_update.get("current_stage", node_name)
                
                # Push the live LangGraph state directly to Redis via Celery!
                self.update_state(
                    state="IN_PROGRESS", 
                    meta={"stage": current_stage, "node": node_name}
                )
                app_logger.info(f"Job {job_id} transitioned to {node_name}")
                
        # If the loop finishes, we return the final success state
        return {"stage": "Complete", "status": "SUCCESS"}
        
    except Exception as e:
        app_logger.error(f"Pipeline failed for {job_id}: {str(e)}")
        # If it crashes, update the state so the frontend knows it failed
        self.update_state(state="FAILED", meta={"error": str(e), "stage": "Failed"})
        raise e