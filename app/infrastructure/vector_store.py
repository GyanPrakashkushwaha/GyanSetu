# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from core.config import OPENAI_API_KEY
from models.database import DocumentChunk
from core.logger import app_logger
from models.database import SessionLocal

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)

    def ingest_chunks(self, job_id: str, chunks: list[dict]):
        app_logger.info(f"Generating Gemini embeddings for {len(chunks)} chunks...")
        
        texts_to_embed = [chunk["content"] for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts_to_embed)
        
        db_chunks = []
        for chunk, vector in zip(chunks, vectors):
            db_chunks.append(
                DocumentChunk(
                    job_id=job_id,
                    header_path=chunk["header_path"],
                    content=chunk["content"],
                    embedding=vector
                )
            )
            
        with SessionLocal() as db:
            db.add_all(db_chunks)
            db.commit()
            
        app_logger.info("Successfully saved vectorized chunks to PostgreSQL.")

vector_store = VectorStore()