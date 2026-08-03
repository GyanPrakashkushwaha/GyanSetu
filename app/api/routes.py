import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from celery.result import AsyncResult
from .celery_app import celery_app

from .worker import run_background_pipeline

router = APIRouter()

class DocumentPayload(BaseModel):
    raw_text: str

@router.post("/jobs/generate", status_code=202)
async def start_generation_job(payload: DocumentPayload):
    job_id = str(uuid.uuid4())
    
    run_background_pipeline.apply_async(args=[job_id, payload.raw_text], task_id=job_id)
    
    return {"job_id": job_id, "message": "Generation task queued."}

@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """The frontend polls this endpoint every ~3 seconds to update its progress bar."""
    
    # Fetch the live task data from Redis
    task = AsyncResult(job_id, app=celery_app)
    
    # If the task is purely pending/not started
    if task.state == 'PENDING':
        return {"job_id": job_id, "status": "PENDING", "stage": "Queued"}
    
    # If the task failed completely
    elif task.state == 'FAILED':
        return {"job_id": job_id, "status": "FAILED", "stage": "Failed", "details": str(task.info)}
    
    # If the task finished successfully
    elif task.state == 'SUCCESS':
        return {"job_id": job_id, "status": "SUCCESS", "stage": "Complete", "details": task.info}
    
    # If the task is in our custom 'IN_PROGRESS' state, extract the meta info we pushed
    else:
        return {
            "job_id": job_id, 
            "status": task.state, 
            "stage": task.info.get("stage", "Unknown") if task.info else "Unknown",
            "details": task.info
        }