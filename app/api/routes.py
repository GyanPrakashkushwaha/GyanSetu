import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from celery.result import AsyncResult
from .celery_app import celery_app

from .worker import run_background_pipeline

router = APIRouter()

class DocumentPayload(BaseModel):
    raw_text: str
    
class ResumePayload(BaseModel):
    human_feedback: str


@router.post("/jobs/generate", status_code=202)
async def start_generation_job(payload: DocumentPayload):
    job_id = str(uuid.uuid4())
    
    run_background_pipeline.apply_async(args=[job_id, payload.raw_text], task_id=job_id)
    
    return {"job_id": job_id, "message": "Generation task queued."}


@router.post("/jobs/{job_id}/resume", status_code=202)
async def resume_generation_job(job_id: str, payload: ResumePayload):
    app_logger.info(f"Received resume request for job {job_id}")
    
    run_background_pipeline.apply_async(
        kwargs={
            "job_id": job_id, 
            "text": None,
            "human_feedback": payload.human_feedback
        }, 
        task_id=f"{job_id}-resume" 
    )
    
    return {"job_id": job_id, "message": "Job successfully queued for resumption."}


@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    try:
        task = AsyncResult(job_id, app=celery_app)
        
        # 1. Handle explicit failure safely
        if task.state == 'FAILURE':
            # task.info contains the exception object here
            error_message = str(task.info) if task.info else "Unknown Pipeline Error"
            return {
                "job_id": job_id,
                "status": "FAILED",
                "stage": "Failed",
                "error": error_message
            }
            
        # 2. Handle successful completion
        elif task.state == 'SUCCESS':
            return {
                "job_id": job_id,
                "status": "SUCCESS",
                "stage": "Completed",
                "result": task.info
            }
            
        # 3. Handle pending state (in queue, hasn't started)
        elif task.state == 'PENDING':
            # task.
             return {
                "job_id": job_id,
                "status": "PENDING",
                "stage": "Queued"
            }
            
        # 4. Handle PROGRESS or custom states
        else:
            # Ensure task.info is a dictionary before calling .get()
            info = task.info if isinstance(task.info, dict) else {}
            return {
                "job_id": job_id,
                "status": task.state,
                "stage": info.get("stage", "Processing"),
                "details": info
            }
            
    except Exception as e:
        logger.error(f"Error retrieving job status for {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching job status.")