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
        
        # Store page images for later use
        self.page_images = {}
        
    def encode_pdf(self, pdf_path: str) -> str:
        """Encode the pdf to base64."""
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: The file {pdf_path} was not found.")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
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
            print(f"Tamaño del PDF en base64: {len(base64_pdf)} caracteres")
            
            try:
                pdf_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_pdf}"
                    },
                    include_image_base64=True  # Important: This ensures images are included
                )
                print("✅ Respuesta de Mistral OCR recibida")
            except Exception as api_error:
                print(f"❌ Error en la llamada a Mistral OCR: {str(api_error)}")
                print(f"📋 Tipo de error: {type(api_error).__name__}")
                raise
            
            # Convertir respuesta a formato JSON
            response_dict = json.loads(pdf_response.model_dump_json())
            print(f"📋 Estructura de respuesta: {list(response_dict.keys())}")
            
            # Extraer el contenido markdown de todas las páginas Y las imágenes
            pages = response_dict.get("pages", [])
            print(f"📋 Número total de páginas detectadas: {len(pages)}")
            
            # Store page images for later use in chunking
            self.page_images = {}
            
            if pages and len(pages) > 0:
                # Concatenar contenido de todas las páginas y extraer imágenes
                markdown_content = ""
                for i, page in enumerate(pages):
                    page_content = page.get("markdown", "")
                    markdown_content += f"\n\n--- Page {i+1} ---\n\n{page_content}"
                    
                    # Extract images from this page - be more flexible with the structure
                    page_images = []
                    
                    # Try different possible locations for images
                    if "images" in page and page["images"]:
                        page_images = page["images"]
                    elif "image_base64" in page and page["image_base64"]:
                        # Sometimes images might be in a different field
                        page_images = [page["image_base64"]] if isinstance(page["image_base64"], str) else page["image_base64"]
                    elif "base64_images" in page and page["base64_images"]:
                        page_images = page["base64_images"]
                    
                    # Store images if found
                    if page_images:
                        self.page_images[i+1] = page_images
                        print(f"✅ Página {i+1}: {len(page_content)} caracteres, {len(page_images)} imágenes almacenadas")
                    else:
                        print(f"✅ Página {i+1}: {len(page_content)} caracteres, sin imágenes")
                
                print(f"✅ Contenido total extraído: {len(markdown_content)} caracteres")
                print(f"✅ Total de páginas con imágenes: {len(self.page_images)}")
                
                for page_num, images in self.page_images.items():
                    print(f"🔍 Página {page_num}: {len(images)} imágenes almacenadas")
                    
            else:
                markdown_content = response_dict.get("content", "")
                print(f"⚠️  Usando fallback 'content': {len(markdown_content)} caracteres")
            
            if not markdown_content:
                print("❌ Error: No se pudo extraer contenido del PDF")
                print(f"📋 Claves disponibles en response_dict: {list(response_dict.keys())}")
                print(f"📋 Número de páginas: {len(pages)}")
                if pages:
                    print(f"📋 Claves de pages[0]: {list(pages[0].keys())}")
                return None
            
            print(f"Contenido extraído exitosamente: {len(markdown_content)} caracteres")
            
            return {
                "markdown_content": markdown_content,
                "response_data": response_dict,
                "original_filename": os.path.basename(pdf_path),
                "page_images": self.page_images
            }
                
        except Exception as e:
            print(f"Error al extraer contenido del PDF: {str(e)}")
            return None
    
    def extract_images_from_chunk(self, chunk_content: str, page_num: int) -> List[str]:
        chunk_images = []
        
        # Get images from the page this chunk belongs to
        page_images = self.page_images.get(page_num, [])
        
        if not page_images:
            return chunk_images
        
        # Strategy 1: If chunk mentions figures/images specifically, include all page images
        image_references = re.findall(
            r'(figura\s*\d+|imagen\s*\d+|gráfico\s*\d+|diagrama\s*\d+|tabla\s*\d+)', 
            chunk_content, 
            re.IGNORECASE
        )
        
        if image_references:
            # Include all images from this page if chunk references figures
            for img in page_images:
                if isinstance(img, dict) and 'image_base64' in img:
                    chunk_images.append(img['image_base64'])
                elif isinstance(img, str):
                    chunk_images.append(img)
            print(f"   Chunk con referencias a imágenes: {len(chunk_images)} imágenes incluidas")
            return chunk_images
        
        # Strategy 2: Include images based on content heuristics
        # If chunk has technical content, mathematical formulas, or structured data
        has_technical_content = any([
            re.search(r'\$.*?\$', chunk_content),  # LaTeX formulas
            re.search(r'\|.*?\|', chunk_content),  # Tables
            len(re.findall(r'\b\d+\.?\d*\b', chunk_content)) > 5,  # Many numbers
            any(keyword in chunk_content.lower() for keyword in [
                'resultado', 'análisis', 'gráfico', 'datos', 'medición', 
                'experimento', 'método', 'proceso', 'sistema'
            ])
        ])
        
        if has_technical_content and page_images:
            # Include first image from page for technical content
            img = page_images[0]
            if isinstance(img, dict) and 'image_base64' in img:
                chunk_images.append(img['image_base64'])
                print(f"   Chunk técnico: 1 imagen incluida")
            elif isinstance(img, str):
                chunk_images.append(img)
        
        return chunk_images
    
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
            # First split by page boundaries
            page_sections = re.split(r'(--- Page \d+ ---)', markdown_content)
            
            # Process pages and their content
            current_page_num = 1
            current_headers = {}
            
            # The first item is content before the first page marker
            if page_sections and not page_sections[0].strip():
                page_sections = page_sections[1:]
            
            i = 0
            while i < len(page_sections):
                section = page_sections[i].strip()
                
                # If this is a page marker, update current page number
                page_match = re.match(r'--- Page (\d+) ---', section)
                if page_match:
                    current_page_num = int(page_match.group(1))
                    i += 1
                    if i >= len(page_sections):
                        break
                    section = page_sections[i].strip()
                
                if not section:
                    i += 1
                    continue
                
                # Process this page's content
                try:
                    # Update headers from this page
                    header_lines = re.findall(r'^(#+)\s+(.*?)$', section, re.MULTILINE)
                    for level, title in header_lines:
                        level_key = f"Header {len(level)}"
                        current_headers[level_key] = title.strip()
                    
                    # Split by headers first
                    header_chunks = self.markdown_splitter.split_text(section)
                    
                    if header_chunks:
                        for chunk in header_chunks:
                            if hasattr(chunk, 'page_content'):
                                content = chunk.page_content
                                metadata = getattr(chunk, 'metadata', {})
                            else:
                                content = str(chunk)
                                metadata = {}
                            
                            # Update metadata with current headers and page number
                            metadata.update({
                                **current_headers,
                                "page_number": current_page_num,
                                "chunk_id": f"{len(chunks)}_0",
                                "chunk_type": "structured_section"
                            })
                            
                            # If chunk is too large, split it further
                            if len(content) > 1200:
                                sub_chunks = self.char_splitter.split_text(content)
                                for j, sub_chunk in enumerate(sub_chunks):
                                    sub_metadata = metadata.copy()
                                    sub_metadata.update({
                                        "chunk_id": f"{len(chunks)}_{j}",
                                        "chunk_type": "text_subdivision",
                                        "parent_chunk": len(chunks)
                                    })
                                    chunks.append({
                                        "content": sub_chunk,
                                        "metadata": sub_metadata
                                    })
                            else:
                                chunks.append({
                                    "content": content,
                                    "metadata": metadata
                                })
                    
                except Exception as e:
                    print(f"Error processing page {current_page_num}: {str(e)}")
                    # Fallback to character-based splitting if header splitting fails
                    sub_chunks = self.char_splitter.split_text(section)
                    for j, sub_chunk in enumerate(sub_chunks):
                        chunks.append({
                            "content": sub_chunk,
                            "metadata": {
                                **current_headers,
                                "page_number": current_page_num,
                                "chunk_id": f"{len(chunks)}_{j}",
                                "chunk_type": "text_subdivision"
                            }
                        })
                
                i += 1
                
        except Exception as e:
            print(f"Error in intelligent_chunking: {str(e)}")
            # Fallback to simple character splitting
            sub_chunks = self.char_splitter.split_text(markdown_content)
            chunks = [{
                "content": chunk,
                "metadata": {
                    "chunk_id": str(i),
                    "chunk_type": "full_text",
                    "page_number": 1
                }
            } for i, chunk in enumerate(sub_chunks)]
        
        return chunks
    
    def extract_visual_elements(self, chunk_content: str) -> Dict[str, Any]:
        visual_info = {
            "has_images": False,
            "has_tables": False,
            "has_formulas": False,
            "has_lists": False
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
        
        # Detectar listas
        list_patterns = [
            r'^\s*[-*+]\s+',     # Unordered lists
            r'^\s*\d+\.\s+',     # Ordered lists
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, chunk_content, re.MULTILINE)
            if matches:
                visual_info["has_lists"] = True
        
        return visual_info
    
    def contextualize_chunk(self, chunk: Dict[str, Any], document_summary: str, 
                          book_title: str, page_num: int = None) -> Dict[str, Any]:
        chunk_content = chunk["content"]
        
        # Use page_num from chunk metadata if not provided
        if page_num is None:
            page_num = chunk.get("metadata", {}).get("page_number", 1)
        
        visual_info = self.extract_visual_elements(chunk_content)
        
        # Extract relevant images for this chunk
        chunk_images = self.extract_images_from_chunk(chunk_content, page_num)
        print(f"Chunk con imágenes: {len(chunk_images)} imágenes incluidas")
        
        # Crear contexto visual
        visual_context = []
        if visual_info["has_images"]:
            visual_context.append(f"Contiene referencias a imágenes/figuras")
        if visual_info["has_tables"]:
            visual_context.append(f"Contiene tablas")
        if visual_info["has_formulas"]:
            visual_context.append(f"Contiene fórmulas")
        if visual_info["has_lists"]:
            visual_context.append(f"Contiene listas")
        if chunk_images:
            visual_context.append(f"Incluye {len(chunk_images)} imágenes asociadas")
        
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
                model="mistral-small-latest",
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
        
        # Enhanced metadata with images
        enhanced_metadata = {
            **chunk.get("metadata", {}),
            "book_title": book_title,
            "page_number": page_num,
            # "images": chunk_images,  # TODO: Add images to metadata
            "has_associated_images": len(chunk_images) > 0,
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
                chunk, document_summary, book_title
            )
            enhanced_chunks.append(enhanced_chunk)
        
        # Summary of images included
        total_chunks_with_images = sum(1 for chunk in enhanced_chunks if chunk["metadata"]["has_associated_images"])
        
        print(f"Proceso completado: {len(enhanced_chunks)} chunks contextualizados")
        print(f"Chunks con imágenes: {total_chunks_with_images}/{len(enhanced_chunks)}")
        
        return enhanced_chunks