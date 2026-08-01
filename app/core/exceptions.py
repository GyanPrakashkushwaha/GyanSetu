class TeacherAIException(Exception):
    """
    Base exception for the Teacher AI Platform.
    All custom exceptions should inherit from this.
    """
    def __init__(self, message: str, status_code: int = 500, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentParsingError(TeacherAIException):
    """Raised when Stage 1 fails to parse a PDF/PPT."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, status_code=422, details=details)

class ExtractionError(TeacherAIException):
    """Raised when Stages 2-3 fail to extract valid metadata or knowledge."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, status_code=500, details=details)

class LLMGenerationError(TeacherAIException):
    """Raised when the LLM gateway fails (e.g., timeouts, rate limits)."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, status_code=502, details=details)
        
class ValidationError(TeacherAIException):
    """Raised in Stage 9 if the generated content fails schema/quality checks."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, status_code=400, details=details)