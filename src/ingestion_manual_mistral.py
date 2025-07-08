import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from embeddings.embedding_funcs import EmbeddingController
from ingestion.ingest_mistral import MistralExtractionController

PDF_PATH = "/Users/jose/Documents/GitHub/ai-genai-dolphin-mistral-qdrant-regulatory-assistant-rag/data/Guia-Tecnica-001-OS-DSR-UTH.pdf"

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

OUTPUT_DIR = Path("./output")

def save_results(enhanced_chunks, output_dir):
    """Guarda los resultados en archivos JSON para inspección"""
    output_dir.mkdir(exist_ok=True)
    
    # Guardar chunks completos
    with open(output_dir / "enhanced_chunks.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_chunks, f, indent=2, ensure_ascii=False)
    
    # Guardar solo contenido contextualizado para revisión
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
    
    print(f"📁 Resultados guardados en: {output_dir}")


# def test_ingestion_process():
#     mistral_controller = MistralExtractionController(api_key=MISTRAL_API_KEY)
#     embedding_controller = EmbeddingController(model_name="nomic-embed-text", pinecone_api_key=PINECONE_API_KEY, pinecone_index=PINECONE_INDEX)

#     print("Procesando documento...")

#     # 1 Paso: Extraccion con Mistral OCR
#     print("1. Extraccion con Mistral OCR...")
#     extraction_result = mistral_controller.extract_content_mistral_ocr(PDF_PATH)
#     if not extraction_result:
#         print("Error en la extracción. Abortando.")
#         return

#     # 2 Paso: Generacion de resumen
#     print("2. Generando resumen general...")
#     document_summary = mistral_controller.generate_document_summary(extraction_result["markdown_content"])
#     print(f"Resumen generado: {document_summary}")


#     # 3. Chunking inteligente
#     print("3. Realizando chunking inteligente...")
#     chunks = mistral_controller.intelligent_chunking(extraction_result["markdown_content"])
#     print(f"Chunking realizado con éxito. {len(chunks)} chunks generados.")

#     # 4. Contextualizar chunks
#     print("4. Contextualizando chunks...")
#     enhanced_chunks = []
#     for chunk in chunks:
#         enhanced_chunk = mistral_controller.contextualize_chunk(
#             chunk, document_summary, "Guia-Tecnica-001-OS-DSR-UTH", 1
#         )
#         enhanced_chunks.append(enhanced_chunk)
#     print(f"Contextualizacion realizada con éxito. {len(enhanced_chunks)} chunks contextualizados.")

#     print("\nEnhanced Chunks: ")
#     for chunk in enhanced_chunks[:5]:
#         print(chunk)

#     # 5. Generacion de embeddings
#     print("5. Generando embeddings...")
#     embeddings = [embedding_controller.generate_embeddings(chunk["content"]) for chunk in enhanced_chunks]
#     print(f"Embeddings generados con éxito. {len(embeddings)} embeddings generados.")

#     # # 6. Almacenamiento en Pinecone
#     # print("6. Almacenando en Pinecone...")
#     # embedding_controller.store_embeddings(embeddings, enhanced_chunks)
#     # print("Almacenamiento en Pinecone completado con éxito.")


def test_full_mistral_pipeline():
    mistral_controller = MistralExtractionController(api_key=MISTRAL_API_KEY)
    embedding_controller = EmbeddingController(
        model_name="nomic-embed-text", 
        pinecone_api_key=PINECONE_API_KEY, 
        pinecone_index=PINECONE_INDEX
    )

    try:
        # Procesar documento completo
        enhanced_chunks = mistral_controller.process_document(
            PDF_PATH, 
            book_title="Guía Técnica 001-OS-DSR-UTH"
        )

        save_results(enhanced_chunks, OUTPUT_DIR)

        print("\n=== EJEMPLO DE CHUNK CONTEXTUALIZADO ===")
        example_chunk = enhanced_chunks[0]
        print(f"Chunk ID: {example_chunk['metadata'].get('chunk_id', 'N/A')}")
        print(f"Tipo: {example_chunk['metadata'].get('chunk_type', 'N/A')}")
        print(f"Elementos visuales: {example_chunk['metadata'].get('visual_summary', 'N/A')}")
        print(f"Contenido: {example_chunk['content'][:300]}...")

        # Generar embeddings
        embeddings = []
        for i, chunk in enumerate(enhanced_chunks):
            print(f"   Generando embedding {i+1}/{len(enhanced_chunks)}")
            embedding = embedding_controller.generate_embeddings(chunk["content"])
            embeddings.append(embedding)

        print(f"\nEmbeddings generados con éxito. {len(embeddings)} embeddings generados.")

        # # Almacenar embeddings
        # embedding_controller.store_embeddings(embeddings, enhanced_chunks)
        # print("Almacenamiento en Pinecone completado con éxito.")

    except Exception as e:
        print(f"Error al procesar el documento: {str(e)}")


if __name__ == "__main__":
    test_full_mistral_pipeline()
    