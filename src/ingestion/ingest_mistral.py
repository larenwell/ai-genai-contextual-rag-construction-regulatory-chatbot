import os
import re
import base64
import json
from mistralai import Mistral
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import Dict, List, Optional, Any


class MistralExtractionController:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.mistral_client = Mistral(api_key=api_key)
        
        # Inicializar text splitters
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"), 
                ("###", "Header 3"),
            ]
        )
        
        self.char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def encode_pdf(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error codificando PDF: {str(e)}")
            return None
    
    def extract_content_mistral_ocr(self, pdf_path: str) -> Optional[Dict[str, str]]:
        try:
            if not os.path.exists(pdf_path):
                print(f"Error: El archivo {pdf_path} no existe")
                return None
                
            print(f"Procesando archivo: {pdf_path}")
            
            # Codificar PDF a base64
            print("Codificando PDF a base64...")
            base64_pdf = self.encode_pdf(pdf_path)
            if not base64_pdf:
                return None
            
            # Llamar a la API OCR
            print("Procesando con Mistral OCR...")
            pdf_response = self.mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                },
                include_image_base64=True
            )
            
            # Convertir respuesta a formato JSON
            response_dict = json.loads(pdf_response.model_dump_json())
            
            # Extraer el contenido markdown
            markdown_content = response_dict.get("content", "")
            
            if not markdown_content:
                print("Error: No se pudo extraer contenido del PDF")
                return None
            
            print(f"Contenido extraído exitosamente: {len(markdown_content)} caracteres")
            
            return {
                "markdown_content": markdown_content,
                "response_data": response_dict,
                "original_filename": os.path.basename(pdf_path)
            }
                
        except Exception as e:
            print(f"Error al extraer contenido del PDF: {str(e)}")
            return None
    
    def generate_document_summary(self, markdown_content: str) -> str:
        try:
            # Limitar el contenido si es muy largo
            content_preview = markdown_content[:8000] if len(markdown_content) > 8000 else markdown_content
            
            summary_response = self.mistral_client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto en análisis de documentos técnicos. Tu tarea es generar un resumen conciso pero completo del documento que capture:
                        
                        1. **Tema principal y objetivos**: ¿De qué trata el documento?
                        2. **Conceptos clave**: Terminología y conceptos importantes
                        3. **Estructura del contenido**: Organización y secciones principales
                        4. **Elementos técnicos**: Tablas, fórmulas, diagramas relevantes
                        5. **Contexto de aplicación**: Ámbito de uso del documento
                        
                        El resumen debe ser útil para contextualizar fragmentos específicos del documento en un sistema RAG."""
                    },
                    {
                        "role": "user", 
                        "content": f"Analiza y resume este documento técnico:\n\n{content_preview}"
                    }
                ]
            )
            
            return summary_response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generando resumen: {str(e)}")
            return "No se pudo generar resumen del documento."
    
    def intelligent_chunking(self, markdown_content: str) -> List[Dict[str, Any]]:
        chunks = []
        
        try:
            # Intentar chunking por headers primero
            header_chunks = self.markdown_splitter.split_text(markdown_content)
            
            if len(header_chunks) > 1:
                print(f"Usando chunking por headers: {len(header_chunks)} chunks")
                base_chunks = header_chunks
            else:
                print("No se encontraron headers, usando chunking por caracteres")
                base_chunks = [{"page_content": markdown_content, "metadata": {}}]
                
        except Exception as e:
            print(f"Error en chunking por headers: {e}")
            base_chunks = [{"page_content": markdown_content, "metadata": {}}]
        
        # Procesar cada chunk base
        for i, chunk in enumerate(base_chunks):
            content = chunk.get("page_content", chunk) if isinstance(chunk, dict) else chunk
            metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
            
            # Si el chunk es muy grande, subdivirlo
            if len(content) > 1200:
                sub_chunks = self.char_splitter.split_text(content)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        "content": sub_chunk,
                        "metadata": {
                            **metadata,
                            "chunk_id": f"{i}_{j}",
                            "chunk_type": "text_subdivision",
                            "parent_chunk": i
                        }
                    })
            else:
                chunks.append({
                    "content": content,
                    "metadata": {
                        **metadata,
                        "chunk_id": str(i),
                        "chunk_type": "structured_section" if metadata else "full_text"
                    }
                })
        
        return chunks
    
    def extract_visual_elements(self, chunk_content: str) -> Dict[str, Any]:
        visual_info = {
            "has_images": False,
            "has_tables": False,
            "has_formulas": False,
            "has_lists": False,
            "image_descriptions": [],
            "table_count": 0,
            "formula_count": 0,
            "list_count": 0
        }
        
        # Detectar imágenes
        image_patterns = [
            r'!\[.*?\]\(.*?\)',  # Markdown images
            r'<img[^>]*>',       # HTML images
            r'imagen\s*\d+',     # Referencias a imágenes
            r'figura\s*\d+',     # Referencias a figuras
        ]
        
        for pattern in image_patterns:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                visual_info["has_images"] = True
                visual_info["image_descriptions"].extend(matches)
        
        # Detectar tablas
        table_patterns = [
            r'\|.*?\|',          # Markdown tables
            r'<table[^>]*>',     # HTML tables
            r'tabla\s*\d+',      # Referencias a tablas
        ]
        
        for pattern in table_patterns:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                visual_info["has_tables"] = True
                visual_info["table_count"] += len(matches)
        
        # Detectar fórmulas
        formula_patterns = [
            r'\$.*?\$',          # LaTeX inline
            r'\$\$.*?\$\$',      # LaTeX block
            r'\\\(.*?\\\)',      # LaTeX parentheses
            r'\\\[.*?\\\]',      # LaTeX brackets
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, chunk_content, re.DOTALL)
            if matches:
                visual_info["has_formulas"] = True
                visual_info["formula_count"] += len(matches)
        
        # Detectar listas
        list_patterns = [
            r'^\s*[-*+]\s+',     # Unordered lists
            r'^\s*\d+\.\s+',     # Ordered lists
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, chunk_content, re.MULTILINE)
            if matches:
                visual_info["has_lists"] = True
                visual_info["list_count"] += len(matches)
        
        return visual_info
    
    def contextualize_chunk(self, chunk: Dict[str, Any], document_summary: str, 
                          book_title: str, page_num: int) -> Dict[str, Any]:
        chunk_content = chunk["content"]
        visual_info = self.extract_visual_elements(chunk_content)
        
        # Crear contexto visual
        visual_context = []
        if visual_info["has_images"]:
            visual_context.append(f"Contiene {len(visual_info['image_descriptions'])} imágenes/figuras")
        if visual_info["has_tables"]:
            visual_context.append(f"Contiene {visual_info['table_count']} tablas")
        if visual_info["has_formulas"]:
            visual_context.append(f"Contiene {visual_info['formula_count']} fórmulas")
        if visual_info["has_lists"]:
            visual_context.append(f"Contiene {visual_info['list_count']} listas")
        
        visual_summary = "; ".join(visual_context) if visual_context else "Solo texto"
        
        # Crear prompt contextual
        context_prompt = f"""
DOCUMENTO: {book_title}
PÁGINA: {page_num}

RESUMEN DEL DOCUMENTO:
{document_summary}

CONTENIDO DEL FRAGMENTO:
{chunk_content}

ELEMENTOS VISUALES: {visual_summary}

INSTRUCCIONES:
Crea un resumen contextualizado de este fragmento que:
1. Explique el contenido en relación al documento completo
2. Preserve la información técnica clave
3. Describa brevemente los elementos visuales si existen
4. Mantenga terminología específica para búsqueda
5. Sea conciso pero informativo (máximo 300 palabras)

IMPORTANTE: Mantén el lenguaje técnico original y conceptos específicos.
"""
        
        try:
            context_response = self.mistral_client.chat.complete(
                model="mistral-small-latest",  # Corregido el modelo
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en crear resúmenes contextualizados para sistemas RAG. Preserva la información técnica y estructura del contenido original."
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ]
            )
            
            contextualized_content = context_response.choices[0].message.content
            
        except Exception as e:
            print(f"Error contextualizando chunk {chunk.get('metadata', {}).get('chunk_id', 'unknown')}: {str(e)}")
            contextualized_content = chunk_content
        
        # Metadata enriquecida
        enhanced_metadata = {
            **chunk.get("metadata", {}),
            "book_title": book_title,
            "page_number": page_num,
            "original_content": chunk_content,
            "contextualized_content": contextualized_content,
            "visual_summary": visual_summary,
            **visual_info
        }
        
        return {
            "content": contextualized_content,
            "metadata": enhanced_metadata
        }
    
    def process_document(self, pdf_path: str, book_title: str = None) -> Optional[List[Dict[str, Any]]]:
        if not book_title:
            book_title = os.path.basename(pdf_path)
        
        print(f"=== Procesando documento: {book_title} ===")
        
        # 1. Extracción OCR
        print("1. Extrayendo contenido con Mistral OCR...")
        extraction_result = self.extract_content_mistral_ocr(pdf_path)
        if not extraction_result:
            return None
        
        # 2. Generar resumen
        print("2. Generando resumen del documento...")
        document_summary = self.generate_document_summary(extraction_result["markdown_content"])
        
        # 3. Chunking inteligente
        print("3. Realizando chunking inteligente...")
        chunks = self.intelligent_chunking(extraction_result["markdown_content"])
        print(f"   Generados {len(chunks)} chunks")
        
        # 4. Contextualizar chunks
        print("4. Contextualizando chunks...")
        enhanced_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"   Procesando chunk {i+1}/{len(chunks)}")
            enhanced_chunk = self.contextualize_chunk(
                chunk, document_summary, book_title, 1
            )
            enhanced_chunks.append(enhanced_chunk)
        
        print(f"Proceso completado: {len(enhanced_chunks)} chunks contextualizados")
        return enhanced_chunks