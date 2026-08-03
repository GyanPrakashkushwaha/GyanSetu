from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4

from core.logger import app_logger
# Assuming you expose your compiled graph as `workflow_app` from your orchestrator
from pipelines.phase3_orchestration.orchestrator import build_tkp_pipeline
from langgraph.checkpoint.postgres import PostgresSaver

# NOTE: In a real app, inject the checkpointer via dependency injection
workflow_app = build_tkp_pipeline(checkpointer)

router = APIRouter(prefix="/api/v1/jobs", tags=["Teacher Knowledge Package"])

# --- Data Contracts (Pydantic Models) ---
class JobStartRequest(BaseModel):
    raw_text: str

class HumanFeedbackRequest(BaseModel):
    feedback: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    current_stage: str
    human_review_required: bool
    validation_errors: List[str]

# --- API Endpoints ---

@router.post("/generate", response_model=JobStatusResponse, status_code=202)
async def start_generation(request: JobStartRequest, background_tasks: BackgroundTasks):
    """Kicks off the asynchronous LangGraph pipeline."""
    job_id = f"job_{uuid4().hex[:8]}"
    
    # 1. Define the initial state exactly as your PipelineState TypedDict expects
    initial_state = {
        "job_id": job_id,
        "raw_text": request.raw_text,
        "retry_count": 0,
        "human_review_required": False,
        "human_feedback": "",
        "period_contents": [],
        "validation_errors": [],
        "current_stage": "Initializing Pipeline"
    }

    # 2. Define the background runner
    def run_graph():
        app_logger.info(f"Background task starting for {job_id}")
        config = {"configurable": {"thread_id": job_id}}
        try:
            workflow_app.invoke(initial_state, config=config)
        except Exception as e:
            app_logger.error(f"Pipeline crashed for {job_id}: {str(e)}")

    # 3. Hand it to FastAPI's background thread pool
    background_tasks.add_task(run_graph)

    # 4. Instantly return the 202 Accepted status to the frontend
    return JobStatusResponse(
        job_id=job_id,
        status="processing",
        current_stage="Initializing Pipeline",
        human_review_required=False,
        validation_errors=[]
    )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """The frontend polls this endpoint every 3 seconds to update its progress bar."""
    config = {"configurable": {"thread_id": job_id}}
    
    # Query our PostgreSQL Checkpointer for the live memory of the graph!
    state_snapshot = workflow_app.get_state(config)
    
    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Job not found or not initialized.")
        
    current_state = state_snapshot.values
    is_complete = current_state.get("current_stage") == "Pipeline Complete"
    
    return JobStatusResponse(
        job_id=job_id,
        status="completed" if is_complete else "processing",
        current_stage=current_state.get("current_stage", "Unknown"),
        human_review_required=current_state.get("human_review_required", False),
        validation_errors=current_state.get("validation_errors", [])
    )


@router.patch("/{job_id}/resume", response_model=JobStatusResponse)
async def resume_with_human_feedback(job_id: str, payload: HumanFeedbackRequest, background_tasks: BackgroundTasks):
    """Hits the LangGraph breakpoint, injects human text, and wakes the graph back up."""
    config = {"configurable": {"thread_id": job_id}}
    
    state_snapshot = workflow_app.get_state(config)
    if not state_snapshot.values.get("human_review_required"):
        raise HTTPException(status_code=400, detail="Job is not currently waiting for human feedback.")

    # 1. Manually update the state dictionary stored in PostgreSQL
    workflow_app.update_state(
        config, 
        {"human_feedback": payload.feedback, "human_review_required": False},
        as_node="human_intervention" # We must tell LangGraph WHICH node is providing this update
    )
    
    # 2. Wake the graph back up in the background (passing None continues from the breakpoint)
    def resume_graph():
        workflow_app.invoke(None, config=config)
        
    background_tasks.add_task(resume_graph)
    
    return JobStatusResponse(
        job_id=job_id,
        status="processing",
        current_stage="Resuming from Human Feedback",
        human_review_required=False,
        validation_errors=state_snapshot.values.get("validation_errors", [])
    )