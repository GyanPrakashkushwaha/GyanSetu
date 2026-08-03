
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    
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
    
class LessonScript(BaseModel):
    introduction: str = Field(..., description="A 3-minute engaging hook to start the class.")
    main_body: List[str] = Field(..., description="Step-by-step teaching points explaining the core concepts.")
    conclusion: str = Field(..., description="A brief summary to wrap up the period.")

class ClassroomActivity(BaseModel):
    title: str = Field(..., description="Catchy title for the activity.")
    duration_minutes: int = Field(..., description="Estimated time for the activity (e.g., 10-15 mins).")
    materials_needed: List[str] = Field(..., description="List of items needed. Return empty list if none.")
    instructions: List[str] = Field(..., description="Step-by-step instructions for the teacher to conduct the activity.")

class FormativeAssessment(BaseModel):
    questions: List[str] = Field(..., description="2-3 quick questions (MCQ or short answer) to test understanding.")
    answer_key: List[str] = Field(..., description="The correct answers for the teacher's reference.")

class PeriodContent(BaseModel):
    period_number: int = Field(..., description="The sequential number of this period (must match the planner).")
    script: LessonScript = Field(..., description="The dialogue and teaching steps.")
    activity: ClassroomActivity = Field(..., description="The engaging classroom activity.")
    assessment: FormativeAssessment = Field(..., description="The end-of-period check for understanding.")

class LearningGap(BaseModel):
    misconception: str = Field(..., description="The specific student misconception identified from the core text.")
    severity_level: SeverityLevel = Field(..., description="The severity of this misconception (Low, Medium, High) based on how fundamentally it blocks future learning of the subject.")
    diagnostic_question: str = Field(..., description="A targeted, thought-provoking question designed specifically to reveal if a student holds this exact misconception. Avoid simple true/false.")
    remedial_action: str = Field(..., description="A concrete, actionable teaching strategy, analogy, or mini-activity the teacher can use to correct this misconception.")

class LearningGapAnalysis(BaseModel):    
    gaps: List[LearningGap] = Field(...,
        description="A comprehensive list of identified learning gaps and their corresponding remediation strategies."
    )
    
class ValidationScorecard(BaseModel):  
    is_hallucinated: bool = Field(..., description="True if the generated content includes facts, figures, or concepts NOT present in the original extracted knowledge base. False if perfectly grounded.")
    pedagogical_score: int = Field(..., ge=1, le=5, description="Score from 1 (terrible) to 5 (excellent) evaluating how well the content matches the target audience's cognitive level and expected tone.")
    feedback_citations: str = Field(..., description="If rejected or hallucinated, provide exact quotes from the generated text and explain why it failed. If approved, write 'N/A'.")
    is_approved: bool = Field(..., description="Final verdict. MUST be True ONLY if is_hallucinated is False AND pedagogical_score is 3 or higher. Otherwise, False.")    

class TeacherKnowledgePackage(BaseModel):
    metadata: EducationalMetadata
    knowledge_base: ExtractedKnowledge
    periods: List[dict] = Field(default_factory=list, description="Placeholder for Stage 4 Teaching Planner.")

class StreamEvent(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the generation job")
    stage: str = Field(..., description="Current LangGraph node or pipeline stage")
    status: str = Field(..., description="State of the stage: IN_PROGRESS, SUCCESS, FAILED, HUMAN_REVIEW_NEEDED")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or node outputs")
    
