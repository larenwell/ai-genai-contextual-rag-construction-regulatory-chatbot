import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from embeddings.embedding_funcs import EmbeddingController
from ingestion.ingest_mistral import MistralExtractionController

PDF_FOLDER_PATH = "../data/test"

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

OUTPUT_DIR = Path("./output")

def save_results(enhanced_chunks, output_dir, pdf_name):
    """Save results in JSON files for inspection"""
    output_dir.mkdir(exist_ok=True)
    
    # Save complete chunks
    with open(output_dir / f"enhanced_chunks_v2_{pdf_name}.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_chunks, f, indent=2, ensure_ascii=False)
    
    # Save only contextualized content for review
    contextualized_content = []
    for i, chunk in enumerate(enhanced_chunks):
        contextualized_content.append({
            "chunk_id": i,
            "content": chunk["content"],
            "metadata": {
                "chunk_type": chunk["metadata"].get("chunk_type", "unknown"),
                "visual_summary": chunk["metadata"].get("visual_summary", ""),
                "has_images": chunk["metadata"].get("has_images", False),
                "has_tables": chunk["metadata"].get("has_tables", False),
                "has_formulas": chunk["metadata"].get("has_formulas", False)
            }
        })
    
    with open(output_dir / "contextualized_content.json", "w", encoding="utf-8") as f:
        json.dump(contextualized_content, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Results saved in: {output_dir}")


def test_full_mistral_pipeline(pdf_path):
    # Previous verifications
    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist")
        return

    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY is not configured")
        return
    
    if not PINECONE_API_KEY:
        print("Error: PINECONE_API_KEY is not configured")
        return

    print(f"File found: {pdf_path}")
    print(f"MISTRAL_API_KEY configured: {'Yes' if MISTRAL_API_KEY else 'No'}")
    print(f"PINECONE_API_KEY configured: {'Yes' if PINECONE_API_KEY else 'No'}")

    mistral_controller = MistralExtractionController(api_key=MISTRAL_API_KEY)
    embedding_controller = EmbeddingController(
        model_name="nomic-embed-text", 
        pinecone_api_key=PINECONE_API_KEY, 
        pinecone_index=PINECONE_INDEX
    )

    try:
        print(f"\n Starting processing of: {pdf_path}")
        enhanced_chunks = mistral_controller.process_document(
            pdf_path, 
            book_title=os.path.basename(pdf_path)
        )

        if enhanced_chunks is None:
            print("Error: process_document returned None. Check previous logs.")
            return

        if len(enhanced_chunks) == 0:
            print("Error: No chunks were generated. Check previous logs.")
            return

        print(f"Processing completed: {len(enhanced_chunks)} chunks generated")
        save_results(enhanced_chunks, OUTPUT_DIR, os.path.basename(pdf_path))

        print("\n=== EXAMPLE CHUNK CONTEXTUALIZED ===")
        example_chunk = enhanced_chunks[0]
        print(f"Chunk ID: {example_chunk['metadata'].get('chunk_id', 'N/A')}")
        print(f"Type: {example_chunk['metadata'].get('chunk_type', 'N/A')}")
        print(f"Visual elements: {example_chunk['metadata'].get('visual_summary', 'N/A')}")
        print(f"Content: {example_chunk['content'][:300]}...")

        # Generate embeddings
        print(f"\n🔄 Generating embeddings for {len(enhanced_chunks)} chunks...")
        embeddings = []
        for i, chunk in enumerate(enhanced_chunks):
            print(f"   Generating embedding {i+1}/{len(enhanced_chunks)}")
            embedding = embedding_controller.generate_embeddings(chunk["content"])
            embeddings.append(embedding)

        print(f"Embeddings generated successfully. {len(embeddings)} embeddings generated.")

        # Store embeddings
        embedding_controller.store_embeddings(embeddings, enhanced_chunks)
        print("Storage in Pinecone completed successfully.")

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        print(f"📋 Full traceback:")
        traceback.print_exc()

# === Operar el pipeline en todos los PDFs de una carpeta ===
def operate_in_folder(pdf_folder_path):
    for pdf_file in os.listdir(pdf_folder_path):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder_path, pdf_file)
            test_full_mistral_pipeline(pdf_path)


if __name__ == "__main__":
    operate_in_folder(PDF_FOLDER_PATH)
    