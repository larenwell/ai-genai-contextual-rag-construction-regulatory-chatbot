import PyPDF2
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter

@dataclass
class TextChunk:
    text: str
    page_number: int
    source: str
    metadata: dict = None

class DocumentExtractionController:
    def __init__(self, pdf_path: str, title: str = None):
        self.pdf_path = Path(pdf_path)
        self.metadata = {
            "source": self.pdf_path.name,
            "total_pages": 0
        }
        self.pdf_title = title

    def _extract_metadata(self, pdf_reader: PyPDF2.PdfReader):
        doc_info = pdf_reader.metadata

        return {
            'title': self.pdf_title,
            # 'author': doc_info.get('/Author', 'Unknown'),
            # 'creator': doc_info.get('/Creator', ''),
            # 'producer': doc_info.get('/Producer', ''),
            'creation_date': datetime.now().strftime('%d-%m-%Y'),
            'modification_date': datetime.now().strftime('%d-%m-%Y')
        }

    def extract_text_from_pdf(self, start_page: int = 0, end_page: int = None) -> List[TextChunk]:
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                self.metadata.update(self._extract_metadata(pdf_reader))
                self.metadata['total_pages'] = len(pdf_reader.pages)
                
                if end_page is None or end_page > self.metadata['total_pages']:
                    end_page = self.metadata['total_pages']

                if start_page >= self.metadata['total_pages']:
                    raise ValueError(f"Start page {start_page} exceeds PDF length of {self.metadata['total_pages']} pages")
                if start_page > end_page:
                    raise ValueError("Start page number cannot be greater than end page number")

                text_chunks = []
                for page_num in range(start_page, end_page):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text.strip():
                        text_chunks.append(TextChunk(
                            text=page_text,
                            page_number=page_num + 1,
                            source=str(self.pdf_path),
                            metadata={
                                **self.metadata,
                                'page_number': page_num + 1
                            }
                        ))
                    else:
                        print(f"Warning: No text extracted from page {page_num + 1}")

                print(f"Extracted {len(text_chunks)} pages of text from {self.metadata['total_pages']} total pages")
                return text_chunks

        except Exception as e:
            print(f"Error processing {self.pdf_path}: {str(e)}")
            raise

    def generate_chunks(self, text_chunks: List[TextChunk]) -> List[TextChunk]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        all_chunks = []
        for chunk in text_chunks:
            split_texts = text_splitter.split_text(chunk.text)
            
            for i, text in enumerate(split_texts):
                new_chunk = TextChunk(
                    text=text,
                    page_number=chunk.page_number,
                    source=chunk.source,
                    metadata={
                        **chunk.metadata,
                        'chunk_id': f"p{chunk.page_number}-{i}",
                        'chunk_index': i,
                        'total_chunks': len(split_texts)
                    }
                )
                all_chunks.append(new_chunk)
        
        return all_chunks