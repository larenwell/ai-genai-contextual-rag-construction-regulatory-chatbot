#!/usr/bin/env python3
"""
Ingestion Integrity Validator
Script para validar la integridad completa de la ingestión de documentos.
Verifica que todos los chunks generados estén correctamente almacenados en Qdrant.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv
import time


def load_generated_chunks(output_dir: str = "src/output/rag") -> Dict[str, int]:
    """Carga y cuenta los chunks generados por archivo"""
    output_path = Path(output_dir)
    if not output_path.exists():
        return {}
    
    file_chunks = {}
    enhanced_files = list(output_path.glob("enhanced_chunks_mistral_*.json"))
    
    for file_path in enhanced_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chunk_count = len(data)
                
                # Extraer nombre del archivo original
                file_name = file_path.name.replace('enhanced_chunks_mistral_', '').replace('.json', '')
                file_chunks[file_name] = chunk_count
                
        except Exception as e:
            print(f"❌ Error leyendo {file_path}: {e}")
    
    return file_chunks


def get_qdrant_chunks_by_file(collection_name: str) -> Tuple[Dict[str, int], int]:
    """Obtiene la distribución de chunks por archivo desde Qdrant con paginación completa"""
    try:
        # Primero obtener el total de puntos en la colección
        count_response = requests.post(
            f"http://localhost:6333/collections/{collection_name}/points/count",
            headers={"Content-Type": "application/json"},
            json={"filter": {}},
            timeout=30
        )
        
        if count_response.status_code != 200:
            print(f"❌ Error obteniendo conteo de puntos: {count_response.status_code}")
            return {}, 0
        
        total_points = count_response.json()["result"]["count"]
        print(f"📊 Total de puntos en Qdrant: {total_points}")
        
        # Implementar paginación para recuperar todos los puntos
        all_points = []
        batch_size = 100  # Tamaño de lote para evitar timeouts
        offset = 0
        
        while offset < total_points:
            response = requests.post(
                f"http://localhost:6333/collections/{collection_name}/points/scroll",
                headers={"Content-Type": "application/json"},
                json={
                    "filter": {},
                    "limit": batch_size,
                    "offset": offset,
                    "with_payload": True,
                    "with_vector": False  # No necesitamos los vectores para validación
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Error recuperando batch {offset//batch_size + 1}: {response.status_code}")
                break
            
            data = response.json()
            batch_points = data["result"]["points"]
            
            if not batch_points:  # No hay más puntos
                break
                
            all_points.extend(batch_points)
            offset += len(batch_points)
            
            print(f"   🔄 Recuperados: {len(all_points)}/{total_points} puntos")
            
            # Evitar sobrecarga en Qdrant
            time.sleep(0.1)
        
        print(f"✅ Total de puntos recuperados: {len(all_points)}")
        
        # Contar por archivo
        file_counts = {}
        for point in all_points:
            metadata = point.get('payload', {})
            book_title = metadata.get('book_title', 'Desconocido')
            file_counts[book_title] = file_counts.get(book_title, 0) + 1
        
        return file_counts, len(all_points)
        
    except Exception as e:
        print(f"❌ Error consultando Qdrant: {e}")
        return {}, 0


def get_qdrant_collection_info(collection_name: str) -> Dict[str, Any]:
    """Obtiene información detallada de la colección en Qdrant"""
    try:
        response = requests.get(
            f"http://localhost:6333/collections/{collection_name}",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()["result"]
        else:
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}


def validate_chunk_metadata_integrity(collection_name: str, sample_size: int = 10) -> Dict[str, Any]:
    """Valida la integridad de la metadata de los chunks"""
    try:
        response = requests.post(
            f"http://localhost:6333/collections/{collection_name}/points/scroll",
            headers={"Content-Type": "application/json"},
            json={"limit": sample_size, "with_payload": True},
            timeout=10
        )
        
        if response.status_code != 200:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
        
        data = response.json()
        points = data["result"]["points"]
        
        # Verificar campos requeridos
        required_fields = ["book_title", "chunk_id", "page_number"]
        validation_results = {
            "total_sampled": len(points),
            "valid_chunks": 0,
            "missing_fields": [],
            "field_coverage": {}
        }
        
        for field in required_fields:
            validation_results["field_coverage"][field] = 0
        
        for point in points:
            metadata = point.get('payload', {})
            is_valid = True
            
            for field in required_fields:
                if field in metadata and metadata[field] is not None:
                    validation_results["field_coverage"][field] += 1
                else:
                    is_valid = False
                    if field not in validation_results["missing_fields"]:
                        validation_results["missing_fields"].append(field)
            
            if is_valid:
                validation_results["valid_chunks"] += 1
        
        # Calcular porcentajes
        for field in required_fields:
            count = validation_results["field_coverage"][field]
            validation_results["field_coverage"][field] = {
                "count": count,
                "percentage": round((count / len(points)) * 100, 1) if points else 0
            }
        
        validation_results["status"] = "success"
        return validation_results
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_integrity_report() -> None:
    """Genera un reporte completo de integridad de la ingestión"""
    print("🔍 VALIDADOR DE INTEGRIDAD DE INGESTIÓN")
    print("=" * 60)
    print(f"📅 Hora de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obtener configuración
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "default-collection")
    
    # 1. Verificar chunks generados
    print("📊 ETAPA 1: VERIFICACIÓN DE CHUNKS GENERADOS")
    print("-" * 60)
    
    generated_chunks = load_generated_chunks()
    total_generated = sum(generated_chunks.values())
    
    if generated_chunks:
        print(f"✅ Archivos procesados encontrados: {len(generated_chunks)}")
        for file_name, count in generated_chunks.items():
            print(f"   📄 {file_name}: {count} chunks")
        print(f"📊 Total de chunks generados: {total_generated}")
    else:
        print("❌ No se encontraron archivos de chunks procesados")
        return
    
    print()
    
    # 2. Verificar información de colección
    print("🗄️ ETAPA 2: VERIFICACIÓN DE COLECCIÓN QDRANT")
    print("-" * 60)
    
    collection_info = get_qdrant_collection_info(collection_name)
    
    if "error" in collection_info:
        print(f"❌ Error accediendo a la colección: {collection_info['error']}")
        return
    
    points_count = collection_info.get('points_count', 0)
    indexed_vectors = collection_info.get('indexed_vectors_count', 0)
    
    print(f"✅ Colección: {collection_name}")
    print(f"📈 Puntos almacenados: {points_count}")
    print(f"🔢 Vectores indexados: {indexed_vectors}")
    print()
    
    # 3. Verificar distribución por archivo en Qdrant
    print("📋 ETAPA 3: VERIFICACIÓN DE DISTRIBUCIÓN EN QDRANT")
    print("-" * 60)
    
    qdrant_chunks, total_retrieved = get_qdrant_chunks_by_file(collection_name)
    
    if qdrant_chunks:
        print(f"✅ Chunks recuperados de Qdrant: {total_retrieved}")
        for file_name, count in qdrant_chunks.items():
            print(f"   📄 {file_name}: {count} chunks")
    else:
        print("❌ No se pudieron recuperar chunks de Qdrant")
        return
    
    print()
    
    # 4. Comparación y análisis de integridad
    print("🔍 ETAPA 4: ANÁLISIS DE INTEGRIDAD")
    print("-" * 60)
    
    # Verificar coincidencia total
    total_match = (total_generated == points_count == total_retrieved)
    print(f"📊 Coincidencia total de chunks: {'✅ SÍ' if total_match else '❌ NO'}")
    print(f"   • Generados: {total_generated}")
    print(f"   • En colección: {points_count}")
    print(f"   • Recuperados: {total_retrieved}")
    print()
    
    # Verificar por archivo
    print("📄 Verificación por archivo:")
    all_files_match = True
    
    for file_name in generated_chunks:
        generated_count = generated_chunks[file_name]
        qdrant_count = qdrant_chunks.get(file_name, 0)
        file_match = (generated_count == qdrant_count)
        
        status = "✅" if file_match else "❌"
        print(f"   {status} {file_name}:")
        print(f"      • Generados: {generated_count}")
        print(f"      • En Qdrant: {qdrant_count}")
        
        if not file_match:
            all_files_match = False
            difference = abs(generated_count - qdrant_count)
            if generated_count > qdrant_count:
                print(f"      ⚠️  Faltan {difference} chunks en Qdrant")
            else:
                print(f"      ⚠️  Hay {difference} chunks extra en Qdrant")
    
    print()
    
    # 5. Verificar integridad de metadata
    print("🏷️ ETAPA 5: VERIFICACIÓN DE METADATA")
    print("-" * 60)
    
    metadata_validation = validate_chunk_metadata_integrity(collection_name, 20)
    
    if metadata_validation["status"] == "success":
        total_sampled = metadata_validation["total_sampled"]
        valid_chunks = metadata_validation["valid_chunks"]
        
        print(f"✅ Muestra validada: {total_sampled} chunks")
        print(f"📊 Chunks válidos: {valid_chunks}/{total_sampled}")
        print()
        print("📋 Cobertura de campos:")
        
        for field, info in metadata_validation["field_coverage"].items():
            status = "✅" if info["percentage"] >= 95 else "⚠️" if info["percentage"] >= 80 else "❌"
            print(f"   {status} {field}: {info['count']}/{total_sampled} ({info['percentage']}%)")
        
        if metadata_validation["missing_fields"]:
            print(f"\n⚠️ Campos con problemas: {', '.join(metadata_validation['missing_fields'])}")
    else:
        print(f"❌ Error validando metadata: {metadata_validation['error']}")
    
    print()
    
    # 6. Resumen final y recomendaciones
    print("📋 RESUMEN FINAL")
    print("=" * 60)
    
    if total_match and all_files_match:
        print("🎉 ¡INTEGRIDAD COMPLETA VERIFICADA!")
        print("   ✅ Todos los chunks fueron ingestados correctamente")
        print("   ✅ La distribución por archivo es correcta")
        print("   ✅ La metadata está presente")
        print()
        print("🚀 El sistema RAG está listo para usar")
    else:
        print("⚠️ SE DETECTARON PROBLEMAS DE INTEGRIDAD")
        print()
        print("🔧 Recomendaciones:")
        
        if not total_match:
            print("   1. Revisar logs de ingestión para errores")
            print("   2. Verificar conectividad con Qdrant")
            print("   3. Considerar re-ejecutar la ingestión")
        
        if not all_files_match:
            print("   4. Re-procesar archivos con discrepancias")
            print("   5. Verificar integridad de archivos JSON generados")
        
        print("   6. Ejecutar: python3 src/ingestion_manual_mistral.py --retry")


def main():
    """Función principal"""
    # Cargar variables de entorno
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    try:
        generate_integrity_report()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Validación interrumpida por el usuario")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
