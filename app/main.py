# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from api.schemas import APIResponse
from core.exceptions import LLMGenerationError, ExtractionError
from core.logger import app_logger

# 1. Bootstrapping the Application
app = FastAPI(
    title="Teacher AI Platform API",
    description="10-Stage Pipeline API for generating Teacher Knowledge Packages (TKP).",
    version="1.0.0"
)

# 2. CORS Middleware (Protecting the perimeter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Note: Restrict this to your frontend URL (e.g., localhost:3000) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Global Exception Handlers (The "Approach C" Magic)
@app.exception_handler(ExtractionError)
async def extraction_error_handler(request: Request, exc: ExtractionError):
    app_logger.error(f"Extraction Error at {request.url.path}: {exc.message}")
    response = APIResponse(
        success=False,
        message="Failed to parse or extract data from the document.",
        error_details=exc.details
    )
    # 422 Unprocessable Entity is semantically correct here
    return JSONResponse(status_code=422, content=response.model_dump())

@app.exception_handler(LLMGenerationError)
async def llm_generation_error_handler(request: Request, exc: LLMGenerationError):
    app_logger.error(f"LLM Error at {request.url.path}: {exc.message}")
    response = APIResponse(
        success=False,
        message="The AI engine failed to generate the pedagogical content.",
        error_details=exc.details
    )
    # 502 Bad Gateway indicates an upstream service (like OpenAI) failed
    return JSONResponse(status_code=502, content=response.model_dump())

@app.exception_handler(Exception)
async def global_500_handler(request: Request, exc: Exception):
    # The ultimate safety net for unhandled bugs
    app_logger.critical(f"Unhandled Server Error: {str(exc)}")
    response = APIResponse(
        success=False,
        message="An unexpected internal server error occurred.",
        error_details=str(exc) # Note: Hide this from the frontend in real production!
    )
    return JSONResponse(status_code=500, content=response.model_dump())


# 4. Mount the Application Routes
app.include_router(api_router, prefix="/api/v1")

# 5. Load Balancer Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Used by Docker/Kubernetes to verify the container is alive."""
    return APIResponse(success=True, message="Teacher AI Platform is fully operational.")