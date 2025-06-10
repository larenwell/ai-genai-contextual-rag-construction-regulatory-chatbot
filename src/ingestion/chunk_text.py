# src/ingestion/chunk_text.py

from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text_file(
    input_txt: Path,
    output_dir: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Divide un archivo de texto en chunks para RAG.
    - input_txt: ruta al .txt limpio (data/cleaned/*.txt).
    - output_dir: carpeta donde se guardarán los chunks (data/chunks/).
    - chunk_size: longitud máxima de cada chunk (caracteres).
    - chunk_overlap: solapamiento entre chunks (caracteres).
    """
    # Leer texto limpio
    text = input_txt.read_text(encoding="utf-8")

    # Configurar el splitter de LangChain
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    # Generar los chunks
    chunks = splitter.split_text(text)

    # Guardar cada chunk como archivo .txt
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(chunks, start=1):
        chunk_file = output_dir / f"{input_txt.stem}_chunk_{i:03}.txt"
        chunk_file.write_text(chunk, encoding="utf-8")
    print(f"→ {len(chunks)} chunks generados en {output_dir}")

def main():
    project_root = Path.cwd()
    clean_dir = project_root/"data"/"cleaned"
    chunks_dir = project_root/"data"/"chunks"

    # Procesar todos los .txt limpios
    for txt_file in clean_dir.glob("*.txt"):
        print(f"Chunking {txt_file.name}...")
        chunk_text_file(txt_file, chunks_dir)

if __name__ == "__main__":
    main()
