#!/usr/bin/env python3
"""
Script to view and analyze metadata structure in output files.
Shows the format and content of processed documents.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and return JSON file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return {}

def analyze_chunk_structure(chunk: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
    """Analyze the structure of a single chunk."""
    analysis = {
        "chunk_id": chunk.get("id", f"chunk_{chunk_index}"),
        "chunk_type": chunk.get("chunk_type", "unknown"),
        "content_length": len(str(chunk.get("content", ""))),
        "enhanced_context_length": len(str(chunk.get("enhanced_context", ""))),
        "page_numbers": chunk.get("page_numbers", []),
        "visual_elements_count": len(chunk.get("visual_elements", [])),
        "metadata_fields": list(chunk.get("metadata", {}).keys()),
        "has_embeddings": "embeddings" in chunk,
        "sample_content": str(chunk.get("content", ""))[:200] + "..." if len(str(chunk.get("content", ""))) > 200 else str(chunk.get("content", "")),
        "sample_context": str(chunk.get("enhanced_context", ""))[:200] + "..." if len(str(chunk.get("enhanced_context", ""))) > 200 else str(chunk.get("enhanced_context", ""))
    }
    return analysis

def analyze_visual_element(element: Dict[str, Any], element_index: int) -> Dict[str, Any]:
    """Analyze the structure of a visual element."""
    if hasattr(element, '__dict__'):  # Dataclass object
        element = element.__dict__
    
    analysis = {
        "element_id": f"element_{element_index}",
        "element_type": element.get("element_type", "unknown"),
        "content_length": len(str(element.get("content", ""))),
        "has_base64": bool(element.get("base64_data")),
        "page_number": element.get("page_number"),
        "has_position": bool(element.get("position")),
        "has_description": bool(element.get("description")),
        "has_technical_info": bool(element.get("technical_info")),
        "has_context": bool(element.get("context")),
        "has_bbox_annotation": bool(element.get("bbox_annotation")),
        "sample_content": str(element.get("content", ""))[:100] + "..." if len(str(element.get("content", ""))) > 100 else str(element.get("content", "")),
        "sample_description": str(element.get("description", ""))[:100] + "..." if len(str(element.get("description", ""))) > 100 else str(element.get("description", ""))
    }
    return analysis

def view_metadata_structure():
    """View and analyze metadata structure in output files."""
    output_dir = Path("./output")
    
    if not output_dir.exists():
        print("❌ Output directory not found")
        return
    
    print("🔍 ANALIZANDO ESTRUCTURA DE METADATOS")
    print("=" * 60)
    
    # Find all JSON files in output directory
    json_files = list(output_dir.glob("*.json"))
    
    if not json_files:
        print("❌ No JSON files found in output directory")
        return
    
    print(f"📁 Encontrados {len(json_files)} archivos JSON:")
    for file in json_files:
        print(f"   - {file.name}")
    
    print("\n" + "=" * 60)
    
    # Analyze each file
    for file_path in json_files:
        print(f"\n📄 ANALIZANDO: {file_path.name}")
        print("-" * 40)
        
        data = load_json_file(str(file_path))
        if not data:
            continue
        
        # Determine file type based on name
        if "enhanced_chunks_annotated" in file_path.name:
            analyze_chunks_file(data, file_path.name)
        elif "document_annotations" in file_path.name:
            analyze_document_annotations(data, file_path.name)
        elif "visual_elements" in file_path.name:
            analyze_visual_elements_file(data, file_path.name)
        elif "processing_result" in file_path.name:
            analyze_processing_result(data, file_path.name)
        elif "contextualized_content" in file_path.name:
            analyze_contextualized_content(data, file_path.name)
        else:
            analyze_generic_json(data, file_path.name)

def analyze_chunks_file(data: Dict[str, Any], filename: str):
    """Analyze enhanced chunks file."""
    print(f"📋 TIPO: Enhanced Chunks Annotated")
    print(f"📊 Total chunks: {len(data)}")
    
    if not data:
        print("❌ No chunks found")
        return
    
    # Analyze first few chunks
    print(f"\n🔍 ANÁLISIS DE CHUNKS (mostrando primeros 3):")
    for i, chunk in enumerate(data[:3]):
        analysis = analyze_chunk_structure(chunk, i)
        print(f"\n   Chunk {i+1}:")
        print(f"     - ID: {analysis['chunk_id']}")
        print(f"     - Tipo: {analysis['chunk_type']}")
        print(f"     - Longitud contenido: {analysis['content_length']}")
        print(f"     - Longitud contexto: {analysis['enhanced_context_length']}")
        print(f"     - Páginas: {analysis['page_numbers']}")
        print(f"     - Elementos visuales: {analysis['visual_elements_count']}")
        print(f"     - Campos metadata: {len(analysis['metadata_fields'])}")
        print(f"     - Tiene embeddings: {analysis['has_embeddings']}")
        print(f"     - Contenido: {analysis['sample_content']}")
        print(f"     - Contexto: {analysis['sample_context']}")
    
    # Show sample chunk structure
    if data:
        print(f"\n📋 ESTRUCTURA COMPLETA DEL PRIMER CHUNK:")
        sample_chunk = data[0]
        print(json.dumps(sample_chunk, indent=2, ensure_ascii=False)[:2000] + "..." if len(json.dumps(sample_chunk, indent=2, ensure_ascii=False)) > 2000 else json.dumps(sample_chunk, indent=2, ensure_ascii=False))

def analyze_document_annotations(data: Dict[str, Any], filename: str):
    """Analyze document annotations file."""
    print(f"📋 TIPO: Document Annotations")
    print(f"📊 Campos: {list(data.keys())}")
    
    print(f"\n📋 CONTENIDO:")
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 200:
            print(f"   {key}: {value[:200]}...")
        else:
            print(f"   {key}: {value}")

def analyze_visual_elements_file(data: List[Dict[str, Any]], filename: str):
    """Analyze visual elements file."""
    print(f"📋 TIPO: Visual Elements")
    print(f"📊 Total elementos: {len(data)}")
    
    if not data:
        print("❌ No visual elements found")
        return
    
    # Analyze first few elements
    print(f"\n🔍 ANÁLISIS DE ELEMENTOS VISUALES (mostrando primeros 3):")
    for i, element in enumerate(data[:3]):
        analysis = analyze_visual_element(element, i)
        print(f"\n   Elemento {i+1}:")
        print(f"     - ID: {analysis['element_id']}")
        print(f"     - Tipo: {analysis['element_type']}")
        print(f"     - Página: {analysis['page_number']}")
        print(f"     - Tiene base64: {analysis['has_base64']}")
        print(f"     - Tiene posición: {analysis['has_position']}")
        print(f"     - Tiene descripción: {analysis['has_description']}")
        print(f"     - Tiene info técnica: {analysis['has_technical_info']}")
        print(f"     - Tiene contexto: {analysis['has_context']}")
        print(f"     - Tiene anotación bbox: {analysis['has_bbox_annotation']}")
        print(f"     - Contenido: {analysis['sample_content']}")
        print(f"     - Descripción: {analysis['sample_description']}")

def analyze_processing_result(data: Dict[str, Any], filename: str):
    """Analyze processing result file."""
    print(f"📋 TIPO: Processing Result")
    print(f"📊 Campos principales: {list(data.keys())}")
    
    if "processing_stats" in data:
        stats = data["processing_stats"]
        print(f"\n📊 ESTADÍSTICAS DE PROCESAMIENTO:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    if "metadata" in data:
        metadata = data["metadata"]
        print(f"\n📋 METADATA:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")

def analyze_contextualized_content(data: Dict[str, Any], filename: str):
    """Analyze contextualized content file."""
    print(f"📋 TIPO: Contextualized Content")
    print(f"📊 Campos: {list(data.keys())}")
    
    print(f"\n📋 CONTENIDO:")
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 200:
            print(f"   {key}: {value[:200]}...")
        else:
            print(f"   {key}: {value}")

def analyze_generic_json(data: Dict[str, Any], filename: str):
    """Analyze generic JSON file."""
    print(f"📋 TIPO: Generic JSON")
    print(f"📊 Estructura: {type(data)}")
    
    if isinstance(data, dict):
        print(f"📊 Campos: {list(data.keys())}")
        print(f"\n📋 CONTENIDO:")
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 200:
                print(f"   {key}: {value[:200]}...")
            else:
                print(f"   {key}: {value}")
    elif isinstance(data, list):
        print(f"📊 Lista con {len(data)} elementos")
        if data:
            print(f"📋 PRIMER ELEMENTO:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False)[:1000] + "..." if len(json.dumps(data[0], indent=2, ensure_ascii=False)) > 1000 else json.dumps(data[0], indent=2, ensure_ascii=False))

def main():
    """Main function."""
    print("🔍 VISUALIZADOR DE METADATOS")
    print("=" * 60)
    print("Este script analiza la estructura de los archivos de salida")
    print("para mostrar el formato de los metadatos procesados.")
    print("=" * 60)
    
    view_metadata_structure()
    
    print("\n" + "=" * 60)
    print("✅ Análisis completado")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Revisa la estructura de los chunks para verificar el formato")
    print("2. Verifica que los elementos visuales tengan la información correcta")
    print("3. Confirma que las anotaciones del documento estén completas")
    print("4. Ejecuta el script de ingesta para procesar más documentos")

if __name__ == "__main__":
    main() 