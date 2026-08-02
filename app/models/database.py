import enum
from typing import Any, Optional
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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
    
    # Pointer to our local Docker volume where the Markdown file lives
    markdown_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Store Stage 2 (EducationalMetadata) as highly efficient JSONB
    educational_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True) 
    
    # Store Stage 3 (ExtractedKnowledge) as highly efficient JSONB
    extracted_knowledge: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus), default=PipelineStatus.UPLOADED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )