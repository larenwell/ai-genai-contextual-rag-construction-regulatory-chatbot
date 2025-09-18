import os
import sys
import json
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from embeddings.embedding_qdrant import EmbeddingControllerQdrant
from ingestion.ingest_mistral import MistralExtractionController

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PDF_FOLDER_PATH = os.getenv("PDF_FOLDER_PATH", "./pdfs")

# Create organized output directory structure
OUTPUT_DIR = project_root / "src" / "output" / "rag"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
log_file = OUTPUT_DIR / f"ingestion_{time.strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_stage_title(title: str, stage_number: int = None):
    """Print a beautiful stage title with visual separators"""
    if stage_number:
        print(f"\n{'='*80}")
        print(f"🚀 ETAPA {stage_number}: {title}")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print(f"🎯 {title}")
        print(f"{'='*80}")


def print_sub_stage(title: str):
    """Print a sub-stage title"""
    print(f"\n📋 {title}")
    print(f"{'-'*60}")


def save_results(enhanced_chunks, output_dir, pdf_name):
    """Save results in JSON files for inspection in the rag output directory"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save complete chunks
    with open(output_dir / f"enhanced_chunks_mistral_{pdf_name}.json", "w", encoding="utf-8") as f:
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

    print(f"File found: {pdf_path}")
    print(f"MISTRAL_API_KEY configured: {'Yes' if MISTRAL_API_KEY else 'No'}")

    mistral_controller = MistralExtractionController(api_key=MISTRAL_API_KEY)
    embedding_controller = EmbeddingControllerQdrant()

    try:
        print_stage_title("PROCESAMIENTO DEL DOCUMENTO", 1)
        print(f"📄 Archivo: {pdf_path}")
        enhanced_chunks = mistral_controller.process_document(
            pdf_path, 
            book_title=os.path.basename(pdf_path)
        )

        if enhanced_chunks is None:
            print("❌ Error: process_document returned None. Check previous logs.")
            return

        if len(enhanced_chunks) == 0:
            print("❌ Error: No chunks were generated. Check previous logs.")
            return

        print(f"✅ Procesamiento completado: {len(enhanced_chunks)} chunks generados")
        save_results(enhanced_chunks, OUTPUT_DIR, os.path.basename(pdf_path))

        print_sub_stage("EJEMPLO DE CHUNK CONTEXTUALIZADO")
        example_chunk = enhanced_chunks[0]
        print(f"   🆔 Chunk ID: {example_chunk['metadata'].get('chunk_id', 'N/A')}")
        print(f"   🏷️  Tipo: {example_chunk['metadata'].get('chunk_type', 'N/A')}")
        print(f"   📝 Contenido: {example_chunk['content'][:200]}...")
        print(f"   🖼️  Resumen Visual: {example_chunk['metadata'].get('visual_summary', 'N/A')}")
        print(f"   🖼️  Tiene Imágenes: {example_chunk['metadata'].get('has_images', False)}")
        print(f"   📊 Tiene Tablas: {example_chunk['metadata'].get('has_tables', False)}")
        print(f"   🧮 Tiene Fórmulas: {example_chunk['metadata'].get('has_formulas', False)}")

        print_stage_title("GENERACIÓN DE EMBEDDINGS", 2)
        # Generate embeddings with retry mechanism
        print(f"🔄 Generando embeddings para {len(enhanced_chunks)} chunks...")
        embeddings = []
        failed_embeddings = 0
        
        for i, chunk in enumerate(enhanced_chunks):
            print(f"   🔄 Generando embedding {i+1}/{len(enhanced_chunks)}")
            
            try:
                embedding = embedding_controller.generate_embeddings(chunk["content"])
                embeddings.append(embedding)
            except Exception as e:
                failed_embeddings += 1
                print(f"      ❌ Error generando embedding {i+1}: {str(e)}")
                # Add a placeholder embedding to maintain index alignment
                embeddings.append([0.0] * 768)  # Default embedding dimension
                print(f"      ⚠️  Usando embedding por defecto para chunk {i+1}")
        
        if failed_embeddings > 0:
            print(f"⚠️  {failed_embeddings} embeddings fallaron, usando valores por defecto")
        
        print(f"✅ Embeddings generados: {len(embeddings)}/{len(enhanced_chunks)} (exitosos)")

        print_stage_title("ALMACENAMIENTO EN QDRANT", 3)
        # Store embeddings with error handling
        try:
            embedding_controller.store_embeddings(embeddings, enhanced_chunks, chunk_metadata=[chunk.get("metadata", {}) for chunk in enhanced_chunks])
            print("✅ Almacenamiento en Qdrant completado exitosamente.")
        except Exception as e:
            print(f"❌ Error almacenando en Qdrant: {str(e)}")
            print(f"⚠️  Los chunks fueron procesados pero no se almacenaron en la base de datos")
            print(f"💡 Recomendación: Verificar conectividad con Qdrant y reintentar")
            raise

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        print(f"📋 Full traceback:")
        traceback.print_exc()

# === Operar el pipeline en todos los PDFs de una carpeta ===
def operate_in_folder(pdf_folder_path):
    pdf_files = [f for f in os.listdir(pdf_folder_path) if f.lower().endswith(".pdf")]
    total_files = len(pdf_files)
    
    print_stage_title(f"PROCESAMIENTO DE CARPETA: {pdf_folder_path}")
    print(f"📁 Total de archivos PDF encontrados: {total_files}")
    
    successful_files = 0
    failed_files = 0
    failed_file_list = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        print(f"\n{'='*60}")
        print(f"📄 ARCHIVO {i}/{total_files}: {pdf_file}")
        print(f"{'='*60}")
        
        try:
            test_full_mistral_pipeline(pdf_path)
            successful_files += 1
            logger.info(f"Archivo {pdf_file} procesado exitosamente")
            print(f"✅ Archivo {pdf_file} procesado exitosamente")
        except Exception as e:
            failed_files += 1
            failed_file_list.append(pdf_file)
            logger.error(f"Error procesando {pdf_file}: {str(e)}")
            print(f"❌ Error procesando {pdf_file}: {str(e)}")
            print(f"⚠️  Continuando con el siguiente archivo...")
        
        if i < total_files:
            print(f"\n{'='*60}")
            print(f"⏳ ESPERANDO 2 SEGUNDOS ANTES DEL SIGUIENTE ARCHIVO...")
            print(f"{'='*60}")
            time.sleep(2)
    
    print_stage_title("PROCESAMIENTO COMPLETADO")
    print(f"📊 RESUMEN FINAL DEL PROCESAMIENTO:")
    print(f"   ✅ Archivos procesados exitosamente: {successful_files}")
    print(f"   ❌ Archivos con errores: {failed_files}")
    print(f"   🎯 Total de archivos procesados: {total_files}")
    
    if failed_files > 0:
        print(f"\n📋 ARCHIVOS CON ERRORES:")
        for failed_file in failed_file_list:
            print(f"      - {failed_file}")
        print(f"\n💡 RECOMENDACIÓN: Reintentar los archivos fallidos más tarde")
        
        # Save failed files list for later retry
        failed_files_path = OUTPUT_DIR / "failed_files.txt"
        with open(failed_files_path, "w", encoding="utf-8") as f:
            for failed_file in failed_file_list:
                f.write(f"{failed_file}\n")
        print(f"📋 Lista de archivos fallidos guardada en: {failed_files_path}")
    
    print(f"\n🎉 PROCESAMIENTO DE CARPETA FINALIZADO")
    print(f"📁 Ruta procesada: {pdf_folder_path}")
    print(f"⏰ Hora de finalización: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def retry_failed_files(pdf_folder_path, failed_files_path=None):
    """Reintenta procesar archivos que fallaron anteriormente"""
    if failed_files_path is None:
        failed_files_path = OUTPUT_DIR / "failed_files.txt"
    
    if not failed_files_path.exists():
        print("❌ No se encontró archivo de archivos fallidos")
        return
    
    with open(failed_files_path, "r", encoding="utf-8") as f:
        failed_files = [line.strip() for line in f.readlines()]
    
    if not failed_files:
        print("✅ No hay archivos fallidos para reintentar")
        return
    
    print_stage_title("REINTENTO DE ARCHIVOS FALLIDOS")
    print(f"📋 Archivos a reintentar: {len(failed_files)}")
    
    successful_retries = 0
    still_failed = []
    
    for i, pdf_file in enumerate(failed_files, 1):
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        print(f"\n{'='*60}")
        print(f"🔄 REINTENTO {i}/{len(failed_files)}: {pdf_file}")
        print(f"{'='*60}")
        
        try:
            test_full_mistral_pipeline(pdf_path)
            successful_retries += 1
            print(f"✅ Archivo {pdf_file} procesado exitosamente en reintento")
        except Exception as e:
            still_failed.append(pdf_file)
            print(f"❌ Error persistente en {pdf_file}: {str(e)}")
        
        if i < len(failed_files):
            print(f"\n⏳ Esperando 3 segundos antes del siguiente reintento...")
            import time
            time.sleep(3)
    
    print_stage_title("REINTENTO COMPLETADO")
    print(f"📊 RESUMEN DEL REINTENTO:")
    print(f"   ✅ Archivos exitosos: {successful_retries}")
    print(f"   ❌ Archivos que siguen fallando: {len(still_failed)}")
    
    if still_failed:
        print(f"   📋 Archivos que requieren atención manual:")
        for failed_file in still_failed:
            print(f"      - {failed_file}")
        
        # Update failed files list
        with open(failed_files_path, "w", encoding="utf-8") as f:
            for failed_file in still_failed:
                f.write(f"{failed_file}\n")
        print(f"📋 Lista actualizada guardada en: {failed_files_path}")


if __name__ == "__main__":
    import sys
    
    # Override PDF_FOLDER_PATH with correct path
    correct_pdf_path = "../data/test"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--retry":
        print("🔄 Modo de reintento activado")
        retry_failed_files(correct_pdf_path)
    else:
        print("🚀 Modo de procesamiento normal")
        print(f"📁 Usando ruta corregida: {correct_pdf_path}")
        operate_in_folder(correct_pdf_path)
    