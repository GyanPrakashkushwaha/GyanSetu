from langchain_text_splitters import MarkdownHeaderTextSplitter
from core.logger import app_logger

class DocumentChunker:
    def __init__(self):
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )

    def chunk_markdown(self, raw_markdown: str) -> list[dict]:
        app_logger.info("Splitting markdown into logical chunks...")
        splits = self.splitter.split_text(raw_markdown)
        
        processed_chunks = []
        for split in splits:
            header_path = " > ".join(split.metadata.values()) if split.metadata else "General Context"
            processed_chunks.append({
                "header_path": header_path,
                "content": split.page_content
            })
            
        return processed_chunks

document_chunker = DocumentChunker()