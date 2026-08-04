This is a fantastic architecture. You’ve successfully blended an asynchronous web framework (FastAPI/Celery) with state-of-the-art agentic orchestration (LangGraph) and top-tier parsing (LlamaIndex). Moving heavy LLM operations to a Celery worker backed by an Upstash Redis broker is exactly how you build scalable, production-grade AI systems.

Here is your world-class, production-ready `README.md`.

---

# GyanSetu - Teacher AI Platform 🎓🤖

**GyanSetu** is an intelligent, async-first "Teacher AI Platform" designed to automate and elevate educational content generation. Built by an AI Engineer for modern educators, the platform ingests raw educational materials and orchestrates a complex, 10-stage AI pipeline to output structured lesson plans, learning gap analyses, and validated educational content.

## 🚀 Live Deployment

* **Frontend:** [Insert Vercel URL Here]
* **Backend API:** [Insert AWS URL Here]
* **Observability Dashboard:** [Insert LangSmith Shared Link / Optional]

---

## 🏗 High-Level Architecture

The system utilizes an asynchronous, event-driven architecture to prevent API timeouts during long-running Agentic workflows.

```mermaid
graph TD
    %% Define Node Styles
    classDef frontend fill:#000,stroke:#fff,stroke-width:2px,color:#fff;
    classDef backend fill:#005571,stroke:#fff,stroke-width:2px,color:#fff;
    classDef worker fill:#37814A,stroke:#fff,stroke-width:2px,color:#fff;
    classDef ai fill:#1C3C3C,stroke:#fff,stroke-width:2px,color:#fff;
    classDef db fill:#3ECF8E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef cache fill:#FF4438,stroke:#fff,stroke-width:2px,color:#fff;

    %% Nodes
    Client[Client / Frontend<br/>Vercel]:::frontend
    API[FastAPI Backend<br/>AWS]:::backend
    Redis[(Upstash Redis<br/>Message Broker)]:::cache
    Worker[Celery Worker<br/>AWS]:::worker
    DB[(Supabase PostgreSQL<br/>State & Storage)]:::db
    
    %% AI Nodes
    subgraph AI Pipeline [LangGraph Orchestration]
        LlamaIndex[LlamaIndex<br/>Parsing & Chunking]:::ai
        LangGraph[LangGraph<br/>State Machine]:::ai
        LLMs[LLM Gateway<br/>OpenAI]:::ai
        VectorStore[(Vector Store<br/>OpenAI emb-3-3072)]:::db
        LangSmith[LangSmith<br/>Observability]:::ai
    end

    %% Flows
    Client -- HTTP POST /task --> API
    API -- Enqueue Task --> Redis
    API -. HTTP 202 Accepted .-> Client
    Redis -- Consume Task --> Worker
    Worker -- Trigger --> LangGraph
    
    LangGraph --> LlamaIndex
    LlamaIndex --> VectorStore
    LangGraph <--> LLMs
    LangGraph -. Logs .-> LangSmith
    
    Worker -- Save Results --> DB
    Client -- HTTP GET /status --> API
    API -- Fetch Status/Result --> DB

```

---

## ⚙️ The 10-Stage AI Pipeline

The core intelligence of GyanSetu is powered by a stateful **LangGraph** orchestrator that manages a strict 10-stage execution pipeline:

1. **Document Ingestion:** Securely receives and temporarily stores uploaded educational material.
2. **Advanced Parsing:** Utilizes **LlamaIndex** to extract clean text and metadata from complex document structures (PDFs, PPTs, etc.).
3. **Semantic Chunking:** Context-aware text chunking designed to preserve educational concepts without breaking sentences.
4. **High-Dimensional Embedding:** Converts chunks into vector representations using OpenAI's `text-embedding-3-large` (3072 dimensions) for granular semantic search.
5. **Information Extraction (Phase 1):** Initial LLM pass to identify target audience, subject matter, and core learning objectives.
6. **Learning Gap Analysis (Phase 2):** Agentic evaluation of the material to identify missing prerequisites or conceptual leaps.
7. **Lesson Planning:** Generation of structured, timed lesson outlines based on the extracted objectives.
8. **Content Generation:** Expansion of the lesson plan into rich, engaging educational content.
9. **LLM-as-a-Judge Validation (Phase 3):** An independent LLM prompt critically evaluates the generated content against the original learning gaps and objectives to ensure accuracy and pedagogic quality.
10. **Final Assembly & Async Delivery:** Merges the validated JSON output, saves it to **Supabase**, and marks the Celery task as `SUCCESS`.

---

## 🧠 Design Decisions & Trade-offs

* **FastAPI + Celery:** LLM generation chains (especially with LlamaIndex parsing and LangGraph loops) can take anywhere from 10 to 60+ seconds. To prevent HTTP timeout errors and ensure a snappy user experience, the API immediately returns a `task_id` while a background Celery worker handles the heavy lifting.
* **LangGraph over Sequential Chains:** Instead of a rigid LangChain `SequentialChain`, LangGraph was chosen to allow for cyclical flows. If the **LLM-as-a-judge** validator fails the content in Stage 9, the graph can route back to Stage 8 for a re-write before finalizing.
* **LlamaIndex for Parsing:** Native LangChain document loaders often struggle with complex formatting. LlamaIndex was integrated specifically for its superior data ingestion and indexing capabilities.

---

## 🌟 Bonus / Advanced Features

* **LLM-as-a-Judge:** Implements a self-reflecting validation layer to guarantee output quality.
* **Enterprise Observability:** Fully integrated with **LangSmith** to trace token usage, agent decisions, and latency bottlenecks.
* **Custom Exception Handling & Logging:** Robust, centralized logging (`app/core/logger.py`) ensures that task failures in the Celery worker are traceable and gracefully reported back to the client/database.
* **High-Fidelity Vectors:** Upgraded to `text-embedding-3-large` (3072 dimensions) for unparalleled retrieval accuracy during RAG operations.

---

## 💻 Local Setup & Installation

### Prerequisites

* Python 3.10+
* Docker & Docker Compose (optional, for containerized running)
* An Upstash Redis account
* A Supabase PostgreSQL database

### 1. Environment Variables

Create a `.env` file in the root directory and populate it with your credentials:

```env
# AI Models & Orchestration
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_key
TAVILY_API_KEY=your_tavily_key

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_key
LANGCHAIN_PROJECT=gyansetu-dev

# Infrastructure
REDIS_URL=rediss://default:your_password@your_upstash_url:port
DATABASE_URL=postgresql://postgres:your_password@db.your_supabase_url:5432/postgres
DB_CONNECTION_STRING=postgresql://postgres:your_password@db.your_supabase_url:5432/postgres

```

### 2. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/gyanprakashkushwaha/gyansetu.git
cd gyansetu
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Running the Application (Locally)

**Terminal 1: Start the Celery Worker**

```bash
celery -A app.api.celery_app.celery_app worker --loglevel=info

```

**Terminal 2: Start the FastAPI Server**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

### 4. Running via Docker (Recommended)

```bash
docker build -t gyansetu .
docker run -p 8000:8000 --env-file .env gyansetu

```

---

*Developed by Gyan Prakash Kushwaha.*
