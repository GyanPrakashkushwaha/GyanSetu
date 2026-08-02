



class TeachingPlanner:
    def __init__(self):
        pass
    
    def extract_metadata(self, raw_markdown: str, job_id: str = None) -> EducationalMetadata:
        job_id = job_id or f"meta_{uuid.uuid4().hex[:8]}"
        
        app_logger.info(
            "Starting Stage 2: Extracting Educational Metadata",
            extra={"extra_info": {"job_id": job_id}}
        )
        
        messages = Prompts.Extraction.EDUCATIONAL_METADATA_TEMPLATE.invoke({
            "text_content": raw_markdown
        })
        
        try:
            return llm_gateway.generate_structured(
                prompt=messages,
                response_model=EducationalMetadata,
                job_id=job_id
            )
        except Exception as e:
            app_logger.error(
                f"Stage 2 Failed: {str(e)}",
                extra={"extra_info": {"job_id": job_id}}
            )
            raise ExtractionError(f"Failed to extract metadata: {str(e)}")