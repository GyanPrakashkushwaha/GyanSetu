

import logging
import os
from pathlib import Path
from typing import Optional
from llama_parse import LlamaParse
from app.core.exceptions import DocumentParsingError

# Setup structured logger for Observability
logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Handles Stage 1: Document Intelligence.
    Converts raw PDFs, PPTs, and DOCX files into structurally preserved Markdown.
    """
    def __init__(self):
        # We pull the API key from our environment/config
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            logger.warning("LLAMA_CLOUD_API_KEY is missing. Parser will fail.")

        # Initialize LlamaParse to prioritize Markdown output and mathematical equations
        self.parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            verbose=True,
            language="en"
        )

    def parse_document(self, file_path: Path) -> str:
        """
        Parses an educational document and extracts structured text.
        
        Args:
            file_path (Path): The local path to the uploaded document.
            
        Returns:
            str: The extracted text formatted in Markdown.
            
        Raises:
            DocumentParsingError: If the parsing engine fails.
        """
        logger.info(f"Starting Document Intelligence on: {file_path.name}")
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Uploaded file missing at {file_path}")

        try:
            # Sync parsing for simplicity; LlamaParse also supports async
            documents = self.parser.load_data(str(file_path))
            
            if not documents:
                raise ValueError("Parser returned an empty document list.")

            # Combine pages into a single Markdown string
            full_markdown = "\n\n".join([doc.text for doc in documents])
            
            logger.info(f"Successfully parsed {file_path.name}. Extracted {len(full_markdown)} characters.")
            return full_markdown
            
        except Exception as e:
            logger.error(f"Stage 1 Parsing failed for {file_path.name}: {str(e)}")
            # Wrap third-party exceptions in our domain-specific exception
            raise DocumentParsingError(f"Failed to parse document: {str(e)}") from e
        