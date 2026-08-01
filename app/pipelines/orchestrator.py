import uuid
from core.logger import app_logger
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from models.schemas import EducationalMetadata, ExtractedKnowledge, TeacherKnowledgePackage
from pipelines.phase1_extraction.extractor import knowledge_extractor
from core.exceptions import ExtractionError
# logger = logging.getLogger(__name__)

class PipelineState(TypedDict):
    job_id : str
    raw_text: str
    metadata: EducationalMetadata | None
    knowledge_base: ExtractedKnowledge | None
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


def route_validation(state: PipelineState) -> str:
    if state.get("validation_errors") and len(state["validation_errors"]) > 0:
        logger.warning("Validation failed, routing back for correction.")
        return "retry_generation"
    return "proceed_to_publish"

def build_tkp_pipeline():
    # workflow
    workflow = StateGraph(PipelineState)
    
    # Nodes
    workflow.add_node("classify", educational_classification_node)
    
    # Edges
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", END)
    
    return workflow.compile()

