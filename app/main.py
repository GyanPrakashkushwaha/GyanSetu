
from pipelines.phase1_extraction.parser import DocumentParser
from pipelines.orchestrator import build_tkp_pipeline
from pathlib import Path
from llama_index.core import SimpleDirectoryReader
import uuid
from rich import print as p
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from models.schemas import EducationalMetadata, ExtractedKnowledge, TeacherKnowledgePackage
from pipelines.phase1_extraction.extractor import knowledge_extractor

if __name__=="__main__":
    # file_path = Path("../samples/c10-science-ch10-eng.pdf")
    # obj = DocumentParser()
    # obj.parse_document(file_path)
    class PipelineState(TypedDict):
        job_id : str
        raw_text: str
        metadata: EducationalMetadata | None
        knowledge_base: ExtractedKnowledge | None
        validation_errors: list[str]
        current_stage: str
        
    documents = SimpleDirectoryReader(input_files=[r"../data/63d00cdb-f5fb-4d86-9a8e-4cea460455f1.md"]).load_data()
    text = documents[0].text
    new_job_id = str(uuid.uuid4())
    initial_state = PipelineState(
        job_id=new_job_id,
        raw_text=text,
        metadata=None,
        knowledge_base=None,
        validation_errors=[],
        current_stage="Initialized"
    )
    workflow = build_tkp_pipeline()
    res = workflow.invoke(initial_state)
    p(res)