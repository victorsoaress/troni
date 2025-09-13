import os
import json
import uuid
from pathlib import Path
import pymupdf4llm

# ========================
# Configurações
# ========================
INPUT_DIR = "docs_pdfs"         
OUTPUT_JSON = "dataset_chunks.json"

def process_pdf(pdf_path: Path):
    """Extrai chunks de um PDF usando pymupdf4llm"""
    chunks = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True)
    dataset = []
    for c in chunks:
        dataset.append({
            "id": str(uuid.uuid4()),
            "text": c["text"],
            "source": pdf_path.name,
            "page": c["page"]
        })
    return dataset

def main():
    all_data = []

    pdf_files = list(Path(INPUT_DIR).glob("*.pdf"))
