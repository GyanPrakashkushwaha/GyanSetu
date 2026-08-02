import uuid
from core.logger import app_logger
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from models.schemas import (EducationalMetadata, 
                            ExtractedKnowledge, 
                            TeacherKnowledgePackage,
                            TeachingPlan)
from pipelines.phase1_extraction.extractor import knowledge_extractor
from pipelines.phase2_generation.planner import teaching_planner

from pipelines.phase1_extraction.chunker import document_chunker
from infrastructure.vector_store import vector_store

from core.exceptions import (ExtractionError, 
                            TeachingPlanError)
from langgraph.checkpoint.postgres import PostgresSaver

class PipelineState(TypedDict):
    job_id : str
    raw_text: str
    metadata: EducationalMetadata | None
    knowledge_base: ExtractedKnowledge | None
    teaching_plan: TeachingPlan | None
    validation_errors: list[str]
    current_stage: str

def educational_classification_node(state: PipelineState) -> dict:
    job_id = state["job_id"]
    
    app_logger.info(
        "Starting Educational Classification", 
        extra={"extra_info": {"job_id": job_id, "stage": 2}}
    )
    try:
        result: EducationalMetadata = knowledge_extractor.extract_metadata(
            raw_markdown=state["raw_text"],
            job_id=job_id
        )
        return {
            "metadata": result,
            "current_stage": "Stage 2 Complete"
        }
    except Exception as e:
        app_logger.error(
            f"Classification failed: {str(e)}", 
            extra={"extra_info": {"job_id": job_id}}
        )
        raise ExtractionError(message="Stage 2 Failed", details={"job_id": job_id})

def knowledge_extraction_node(state: PipelineState) -> dict:
    job_id = state["job_id"]
    
    app_logger.info(
        "Starting Knowledge Extraction", 
        extra={"extra_info": {"job_id": job_id, "stage": 3}}
    )
    try:
        result: ExtractedKnowledge = knowledge_extractor.extract_knowledge(
            metadata_json=state["metadata"],
            raw_markdown=state["raw_text"],
            job_id=job_id
        )
        return {
            "knowledge_base": result,
            "current_stage": "Stage 3 Complete"
        }
    except Exception as e:
        app_logger.error(
            f"Extraction failed: {str(e)}", 
            extra={"extra_info": {"job_id": job_id}}
        )
        raise ExtractionError(message="Stage 3 Failed", details={"job_id": job_id})


def vectorization_node(state: PipelineState) -> dict:
    job_id = state["job_id"]
    
    app_logger.info(
        "Starting Document Vectorization", 
        extra={"extra_info": {"job_id": job_id, "stage": 3.5}}
    )
    try:
        chunks = document_chunker.chunk_markdown(state["raw_text"])
        vector_store.ingest_chunks(job_id=job_id, chunks=chunks)
        return {
            "current_stage": "Stage 3.5 Complete"
        }
        
    except Exception as e:
        app_logger.error(
            f"Vectorization failed: {str(e)}", 
            extra={"extra_info": {"job_id": job_id}}
        )
        raise ExtractionError(message="Stage 3.5 Failed", details={"job_id": job_id})


def teaching_planner_node(state: PipelineState) -> dict:
    job_id = state["job_id"]
    
    app_logger.info(
        "Starting Teaching Planning", 
        extra={"extra_info": {"job_id": job_id, "stage": 4}}
    )
    try:
        result: TeachingPlan = teaching_planner.planner(
            metadata_json=state["metadata"],
            extracted_knowledge=state["knowledge_base"],
            job_id=job_id
        )
        return {
            "teaching_plan": result,
            "current_stage": "Stage 4 Complete"
        }
    except Exception as e:
        app_logger.error(
            f"Planning failed: {str(e)}", 
            extra={"extra_info": {"job_id": job_id}}
        )
        raise TeachingPlanError(message="Stage 4 Failed", details={"job_id": job_id})


def route_validation(state: PipelineState) -> str:
    if state.get("validation_errors") and len(state["validation_errors"]) > 0:
        app_logger.warning("Validation failed, routing back for correction.")
        return "retry_generation"
    return "proceed_to_publish"

def build_tkp_pipeline(checkpointer: PostgresSaver):
    print('API CALL MADE')
    workflow = StateGraph(PipelineState)
    
    workflow.add_node("classify", educational_classification_node)
    workflow.add_node("extract", knowledge_extraction_node)
    workflow.add_node("vectorize", vectorization_node)
    workflow.add_node("plan", teaching_planner_node)
    
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "vectorize")  
    workflow.add_edge("vectorize", "plan") 
    workflow.add_edge("plan", END)
    return workflow.compile(checkpointer=checkpointer)