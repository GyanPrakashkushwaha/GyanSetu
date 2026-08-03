
@router.get("/{job_id}/status")
async def get_job_status(job_id: str, checkpointer: PostgresSaver = Depends(get_checkpointer)):
    # Now this endpoint is perfectly isolated and thread-safe!
    workflow = build_tkp_pipeline(checkpointer)
    # ... logic continues