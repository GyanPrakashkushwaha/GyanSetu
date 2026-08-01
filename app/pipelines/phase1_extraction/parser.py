import os
import base64
import json
import io
import httpx
from pathlib import Path
from typing import Optional, Dict, Any

from llama_cloud import LlamaCloud
from core.logger import app_logger
from core.exceptions import DocumentParsingError
from core.config import LLAMA_CLOUD_API_KEY

class DocumentParser:
    def __init__(self):
        self.FILE_ID = None
        if not LLAMA_CLOUD_API_KEY:
            app_logger.warning(
                "LLAMA_CLOUD_API_KEY is missing. Parser will fail.", 
                extra={"extra_info": {"component": "DocumentParser"}}
            )
        
        self.client = LlamaCloud(api_key=LLAMA_CLOUD_API_KEY)

    def parse_document(self, file_path: Path) -> str:
        app_logger.info(
            "Starting Document Intelligence", 
            extra={"extra_info": {"file_name": file_path.name}}
        )
        
        if not file_path.exists():
            app_logger.error(
                "File not found", 
                extra={"extra_info": {"file_path": str(file_path)}}
            )
            raise FileNotFoundError(f"Uploaded file missing at {file_path}")
            
        try:
            file = self.client.files.create(file=file_path, purpose="parse")
            self.FILE_ID = file.id
            
            result = self.client.parsing.parse(
                file_id=file.id,
                tier="agentic",
                version="latest",
                expand=["images_content_metadata", "markdown_full"],
                processing_options={"cost_optimizer": {"enable": True}}
            )
            
            full_markdown = result.markdown_full
            print(full_markdown)
            Path(f"../data/{self.FILE_ID}.md").write_text(full_markdown or "", encoding="utf-8")
            
            b64_str_lst = {}
            if result.images_content_metadata:
                for i, image_meta in enumerate(result.images_content_metadata.images):
                    url = image_meta.presigned_url
                    data_url = self._url_to_base64(url) 
                    key = image_meta.filename.split(".")[0]
                    b64_str_lst[key] = data_url
                    
                with open(f"../data/{self.FILE_ID}.json", "w") as f:
                    json.dump(b64_str_lst, f, indent=4)
                    
            app_logger.info(
                "Successfully parsed document", 
                extra={
                    "extra_info": {
                        "file_name": file_path.name,
                        "file_id": self.FILE_ID,
                        "characters_extracted": len(full_markdown or "")
                    }
                }
            )
            return full_markdown
        
        except Exception as e:
            app_logger.error(
                f"Stage 1 Parsing failed: {str(e)}", 
                extra={"extra_info": {"file_name": file_path.name}}
            )
            raise DocumentParsingError(
                message="Failed to parse document",
                details={"error": str(e), "file_name": file_path.name}
            ) from e

    def _url_to_base64(self, url: str) -> str:
        try:
            response = httpx.get(url)
            response.raise_for_status()

            image_bytes = io.BytesIO(response.content).read()
            base64_string = base64.b64encode(image_bytes).decode("utf-8")

            mime_type = "image/jpeg"
            data_url = f"data:{mime_type};base64,{base64_string}"
            return data_url
            
        except httpx.HTTPError as e:
            app_logger.error(
                f"HTTP error during image download: {str(e)}", 
                extra={"extra_info": {"url": url}}
            )
            raise DocumentParsingError(
                message="Failed to download image from presigned URL",
                details={"error": str(e), "url": url}
            ) from e
            
        except Exception as e:
            app_logger.error(
                f"Image processing failed: {str(e)}", 
                extra={"extra_info": {"url": url}}
            )
            raise DocumentParsingError(
                message="Failed to convert image to base64",
                details={"error": str(e), "url": url}
            ) from e