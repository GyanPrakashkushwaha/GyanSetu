import enum
import os
from typing import Any, Optional
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, func, ForeignKey, Text, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
from core.config import DB_CONNECTION_STRING

engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise e
    
# ---------------------------------------------------------

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 models."""
    pass

class PipelineStatus(str, enum.Enum):
    """Tracks the progress of a document through our pipeline."""
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"           # Stage 1 Complete
    CLASSIFIED = "CLASSIFIED"   # Stage 2 Complete
    EXTRACTED = "EXTRACTED"     # Stage 3 Complete
    FAILED = "FAILED"

class Document(Base):
    """
    Core relational table for storing document state, file pointers, 
    and structured JSON data from our AI pipeline.
    """
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    educational_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True) 
    extracted_knowledge: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus), default=PipelineStatus.UPLOADED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    job_id: Mapped[str] = mapped_column(String(255), index=True) 
    
    header_path: Mapped[str] = mapped_column(String(512), nullable=True) 
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Gemini Gemini Embedding 2 uses 3072 dimensions
    embedding = mapped_column(Vector(3072))