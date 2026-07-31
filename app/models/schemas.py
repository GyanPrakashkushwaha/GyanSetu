
from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# PHASE 1: Extraction & Classification Models
# ==========================================

class EducationalMetadata(BaseModel):
    """Stage 2: Educational Classification """
    subject: str = Field(..., description="The primary academic subject (e.g., Physics, History).")
    grade: str = Field(..., description="The target grade or education level (e.g., 10th Grade, Undergraduate).")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, or Advanced.")
    topic: str = Field(..., description="The specific topic being covered.")
    chapter: str = Field(..., description="The broader chapter this topic belongs to.")
    category: str = Field(..., description="Category of the document (e.g., STEM, Humanities).")
    language: str = Field(default="English", description="The language of the document.")

class ExtractedKnowledge(BaseModel):
    """Stage 3: Structured Educational Representation """
    learning_objectives: List[str] = Field(..., description="Clear, actionable objectives students should achieve.")
    prerequisites: List[str] = Field(..., description="What students must know before this lesson.")
    concepts: List[str] = Field(..., description="Core concepts discussed in the text.")
    definitions: dict[str, str] = Field(..., description="Key terms and their precise definitions.")
    formulae: Optional[List[str]] = Field(default_factory=list, description="Any mathematical or scientific formulas found.")
    misconceptions: List[str] = Field(..., description="Common student misconceptions related to this topic.")

# ==========================================
# MASTER TKP MODEL (The Final Output)
# ==========================================

class TeacherKnowledgePackage(BaseModel):
    """
    Stage 10: The final compiled package representing the 
    Master TeacherKnowledgePackage.json.
    """
    metadata: EducationalMetadata
    knowledge_base: ExtractedKnowledge
    # We will define PeriodPlan, Activities, and Assessments as we build Phase 2!
    periods: List[dict] = Field(default_factory=list, description="Placeholder for Stage 4 Teaching Planner.")