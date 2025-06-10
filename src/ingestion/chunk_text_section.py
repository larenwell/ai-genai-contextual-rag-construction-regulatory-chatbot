# src/ingestion/chunk_text_section.py

import re
from pathlib import Path
from langchain.text_splitter import TokenTextSplitter

# Patrón para detectar encabezados de sección
SECTION_PATTERN = re.compile(
    r'(TÍTULO\s+[IVX]+|CAPÍTULO\s+[IVX]+|Artículo\s+\d+\.)',
    flags=re.IGNORECASE
)

def split_into_sections(text: str) -> list[str]:
    parts = re.split(SECTION_PATTERN, text)
    sections = []

    # Captura preámbulo si existe
    pre = parts[0].strip()
    if pre:
        sections.append(pre)

    # Une cada header con su contenido
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        sections.append(f"{header}\n{content}")

    return sections

def section_and_token_chunks(
    text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
    encoding_name: str = "cl100k_base"   # compatible con modelos HF
) -> list[str]:
    """
    1) Separa en secciones semánticas.
    2) Para cada sección, la vuelve a chunkear por tokens
       asegurando ≤ max_tokens, con overlap.
    """
    sections = split_into_sections(text)

    # Configuramos un splitter basado en tokens
    token_splitter = TokenTextSplitter(
        encoding_name=encoding_name,
        chunk_size=max_tokens,
        chunk_overlap=overlap_tokens
    )

    chunks = []
    for sec in sections:
        # TokenTextSplitter hará tanto secciones < max como sub-chunks
        chunks.extend(token_splitter.split_text(sec))
    return chunks

def chunk_text_file(
    input_txt: Path,
    output_dir: Path
):
    text = input_txt.read_text(encoding="utf-8")
    chunks = section_and_token_chunks(text)

    output_dir.mkdir(parents=True, exist_ok=True)
    for idx, chunk in enumerate(chunks, 1):
        path = output_dir / f"{input_txt.stem}_chunk_{idx:03}.txt"
        path.write_text(chunk, encoding="utf-8")
    print(f"→ {len(chunks)} chunks generados en {output_dir}")

def main():
    project_root = Path.cwd()
    clean_dir = project_root / "data" / "cleaned"
    chunks_dir = project_root / "data" / "chunks_sections"

    for txt_file in sorted(clean_dir.glob("*.txt")):
        print(f"Section+token chunking de {txt_file.name}…")
        chunk_text_file(txt_file, chunks_dir)

if __name__ == "__main__":
    main()
