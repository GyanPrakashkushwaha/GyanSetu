
from pipelines.phase1_extraction.parser import DocumentParser
from pathlib import Path

if __name__=="__main__":
    file_path = Path("../samples/c10-science-ch10-eng.pdf")
    obj = DocumentParser()
    obj.parse_document(file_path)