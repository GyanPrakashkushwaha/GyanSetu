teacher-ai-platform/
├── app/
│   ├── main.py                     # FastAPI application instance & lifespan events
│   ├── api/                        # API Gateway: Routing and HTTP handlers [cite: 23]
│   │   ├── routes.py               
│   │   └── dependencies.py         # Dependency injection (DB sessions, Redis clients)
│   ├── core/                       # App-wide settings and Observability [cite: 42]
│   │   ├── config.py               # Pydantic BaseSettings (Env vars)
│   │   ├── logger.py               # Structured logging and tracing configuration
│   │   └── exceptions.py           # Custom exception handlers
│   ├── models/                     # Data contracts and schemas
│   │   ├── domain.py               # Internal business models
│   │   └── schemas.py              # Pydantic models for API Validation/JSON schema adherence [cite: 20]
│   ├── infrastructure/             # External system integrations (Interfaces)
│   │   ├── redis_client.py         # Progress streaming and caching [cite: 41]
│   │   ├── vector_store.py         # RAG & Traceability setup [cite: 39]
│   │   └── llm_gateway.py          # Centralized LLM API calls with retry mechanisms [cite: 42]
│   ├── pipelines/                  # Core Business Logic: The 10-Stage Pipeline [cite: 7]
│   ├── orchestrator.py   
│   │   ├── phase1_extraction/      # Stages 1-3: Document Intelligence & Classification [cite: 8, 10, 11]
│   │   │   ├── parser.py           
│   │   │   └── extractor.py        
│   │   ├── phase2_generation/      # Stages 4-8: Pedagogical Planning & Content Gen [cite: 13, 14]
│   │   │   ├── planner.py          
│   │   │   ├── content_gen.py      
│   │   │   └── assessment_gen.py   # Rubrics and MCQs [cite: 17]
│   │   └── phase3_orchestration/   # Stages 9-10: Validation, Output, and Orchestration [cite: 20]
│   │       ├── validator.py        # Hallucination detection and completeness checks [cite: 20]
│   │       ├── publisher.py        # Master TeacherKnowledgePackage.json compilation [cite: 21]
│   │       └── progress_stream.py  # Orchestrator for the Streaming Progress API [cite: 22]
│   └── utils/                      # Helper functions (text cleaning, file I/O)
├── tests/                          # Systematic testing (Unit and Integration)
├── samples/                        # Output directory for the 2 sample TKP JSON files [cite: 29]
├── docker-compose.yml              # Multi-container orchestration (FastAPI, Redis, VectorDB)
├── Dockerfile                      # Application containerization
├── requirements.txt                # Python dependencies
└── README.md                       # Setup, high-level architecture diagram, and orchestration explanation [cite: 27, 28]