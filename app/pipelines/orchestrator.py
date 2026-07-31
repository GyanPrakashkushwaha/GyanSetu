
import uuid
from app.core.logger import app_logger
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from app.models.schemas import EducationalMetadata, ExtractedKnowledge, TeacherKnowledgePackage

logger = logging.getLogger(__name__)

class PipelineState(TypedDict):
    job_id : str
    raw_text: str
    metadata: EducationalMetadata | None
    knowledge_base: ExtractedKnowledge | None
    validation_errors: list[str]
    current_stage: str

# Stage 2: Educational Classification
def educational_classification_node(state: PipelineState) -> dict:
    job_id = state["job_id"]
    
    app_logger.info(
        "Starting Educational Classification", 
        extra={"extra_info": {"job_id": job_id, "stage": 2}}
    )
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    structured_llm = llm.with_structured_output(EducationalMetadata)
    
    prompt = f"Analyze the following educational text and classify it:\n\n{state['raw_text']}"
    
    try:
        result: EducationalMetadata = structured_llm.invoke(prompt)
        
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

def trigger_pipeline(text: str):
    new_job_id = str(uuid.uuid4())
    initial_state = PipelineState(
        job_id=new_job_id,
        raw_text=text,
        metadata=None,
        knowledge_base=None,
        validation_errors=[],
        current_stage="Initialized"
    )
    
    wkflow = build_tkp_pipeline()
    # wkflow.invoke(PipelineState)