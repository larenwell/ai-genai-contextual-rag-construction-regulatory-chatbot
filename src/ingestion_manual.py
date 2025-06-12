import os
import sys
import glob
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from llm.context_llm import LLMContext
from embeddings.embedding_funcs import EmbeddingController
from ingestion.ingest_funcs import DocumentExtractionController

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

DATA_DIR = project_root / "data"
PDF_PATTERN = "*.pdf"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

print(PINECONE_API_KEY)
print(PINECONE_INDEX)

@dataclass
class TextChunk:
    text: str
    page_number: int
    source: str
    metadata: dict

def process_pdf(pdf_path, embedding_admin, llm_dolphin):
    print(f"\nProcessing: {Path(pdf_path).name}")
    reading = DocumentExtractionController(pdf_path)
    
    # Extract text and generate chunks
    text_chunks = reading.extract_text_from_pdf()
    original_chunks = reading.generate_chunks(text_chunks)
    
    if not original_chunks:
        print(f"Warning: No text extracted from {pdf_path}")
        return [], []

    # Generate main idea for this document
    text_extracted = "\n".join([chunk.text for chunk in original_chunks])
    text_main_idea = llm_dolphin.generate_main_text_idea(text_extracted)

    # Process each chunk
    contextualized_chunks = []
    for i, chunk in enumerate(original_chunks, 1):
        contextualized_text = llm_dolphin.generate_chunk_context(
            main_idea=text_main_idea, 
            chunk=chunk.text
        )

        contextualized_chunks.append(TextChunk(
            text=contextualized_text,
            page_number=chunk.page_number,
            source=chunk.source,
            metadata=chunk.metadata
        ))
        print(f"  Processed chunk {i}/{len(original_chunks)}")

    # Generate embeddings
    embeddings = [embedding_admin.generate_embeddings(chunk.text) 
                 for chunk in contextualized_chunks]
    
    return embeddings, contextualized_chunks

def main():
    embedding_admin = EmbeddingController(model_name="nomic-embed-text", pinecone_api_key=PINECONE_API_KEY, pinecone_index=PINECONE_INDEX)
    llm_dolphin = LLMContext()

    pdf_files = glob.glob(os.path.join(DATA_DIR, PDF_PATTERN))

    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files to process")

    # Process each PDF
    all_embeddings = []
    all_metadata = []
    all_chunks = []
    
    for pdf_path in pdf_files:
        embeddings, chunks = process_pdf(pdf_path, embedding_admin, llm_dolphin)
        all_embeddings.extend(embeddings)
        all_chunks.extend([c.text for c in chunks])
        all_metadata.extend([c.metadata for c in chunks])
    
    # Store all embeddings in Pinecone
    if all_embeddings:
        print(f"\nStoring {len(all_embeddings)} chunks in Pinecone...")
        embedding_admin.store_embeddings(
            embeddings=all_embeddings,
            chunks=all_chunks,
            chunk_metadata=all_metadata
        )
        print("Done!")
    else:
        print("No embeddings were generated.")


if __name__ == "__main__":
    main()
