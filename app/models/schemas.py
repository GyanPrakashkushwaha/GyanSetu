
from pydantic import BaseModel, Field
from typing import List, Optional

class EducationalMetadata(BaseModel):
    subject: str = Field(..., description="The primary academic subject (e.g., Physics, History).")
    grade: str = Field(..., description="The target grade or education level (e.g., 10th Grade, Undergraduate).")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, or Advanced.")
    topic: str = Field(..., description="The specific topic being covered.")
    chapter: str = Field(..., description="The broader chapter this topic belongs to.")
    category: str = Field(..., description="Category of the document (e.g., STEM, Humanities).")
    language: str = Field(default="English", description="The language of the document.")

class KeyTerm(BaseModel):
    term: str = Field(description="The vocabulary word or key term.")
    definition: str = Field(description="The precise definition of the term.")

class ExtractedKnowledge(BaseModel):
    learning_objectives: List[str] = Field(..., description="Clear, actionable objectives students should achieve.")
    prerequisites: List[str] = Field(..., description="What students must know before this lesson.")
    concepts: List[str] = Field(..., description="Core concepts discussed in the text.")
    key_terms: List[KeyTerm] = Field(..., description="Key terms and their precise definitions.")
    formulae: List[str] = Field(..., description="Any mathematical or scientific formulas found. Return an empty list if none exist.")
    misconceptions: List[str] = Field(..., description="Common student misconceptions related to this topic.")

class TeachingPeriod(BaseModel):
    period_number: int = Field(..., description="The sequential number of the period.")
    focus_topic: str = Field(..., description="The main overarching concept for this period.")
    learning_outcome: str = Field(..., description="What students will be able to do by the end.")
    concepts_covered: List[str] = Field(..., description="Specific extracted concepts covered here.")
    estimated_minutes: int = Field(default=40, description="Standard duration of the period.")

class TeachingPlan(BaseModel):
    total_periods: int = Field(..., description="Total number of periods generated.")
    rationale: str = Field(..., description="Brief pedagogical reasoning for this pacing strategy.")
    periods: List[TeachingPeriod] = Field(..., description="The ordered sequence of teaching periods.")
    
# class ContentGeneration(BaseModel):

class TeacherKnowledgePackage(BaseModel):
    metadata: EducationalMetadata
    knowledge_base: ExtractedKnowledge
    periods: List[dict] = Field(default_factory=list, description="Placeholder for Stage 4 Teaching Planner.")