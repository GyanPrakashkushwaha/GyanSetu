import uuid
from pathlib import Path
from rich import print as p
from typing import TypedDict
import psycopg_pool

from llama_index.core import SimpleDirectoryReader
from langgraph.checkpoint.postgres import PostgresSaver

from pipelines.phase1_extraction.parser import DocumentParser
from pipelines.orchestrator import build_tkp_pipeline
from models.schemas import EducationalMetadata, ExtractedKnowledge
from core.config import DB_CONNECTION_STRING 

class PipelineState(TypedDict):
    job_id : str
    raw_text: str
    metadata: EducationalMetadata | None
    knowledge_base: ExtractedKnowledge | None
    validation_errors: list[str]
    current_stage: str

if __name__=="__main__":
    # from sqlalchemy import text
    # from models.database import engine, Base
    # from core.logger import app_logger

    # def init_database():
    #     app_logger.info("Connecting to database to sync schemas...")
        
    #     with engine.connect() as conn:
    #         # 1. CRITICAL: Enable the pgvector extension FIRST
    #         app_logger.info("Enabling pgvector extension...")
    #         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    #         conn.commit()
            
    #     # 2. Create the tables (this translates your Python classes into SQL CREATE TABLE commands)
    #     app_logger.info("Creating tables...")
    #     Base.metadata.create_all(bind=engine)
        
    #     app_logger.info("Database sync complete! 'document_chunks' table is ready.")

    # # Run the initialization
    # init_database()
    
    
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
    
    with psycopg_pool.ConnectionPool(conninfo=DB_CONNECTION_STRING, kwargs={"autocommit": True}) as pool:
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        workflow = build_tkp_pipeline(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": new_job_id}}
        
        res = workflow.invoke(initial_state, config=config)
        p(res)