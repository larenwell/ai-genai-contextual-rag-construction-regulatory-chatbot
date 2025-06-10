#!/usr/bin/env python3
"""
Orquesta todo el pipeline de indexado:
1) extract_text.py
2) clean_text.py
3) chunk_text_section.py
4) embedder.py
5) qdrant_uploader.py
"""

import sys
import subprocess
from pathlib import Path

# Ajusta la ruta si tu scripts están en otro lugar
SRC_DIR = Path(__file__).parent.parent / "src"

def run(cmd: list[str]):
    print(f"▶️  Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    # 1) Extracción
    run([sys.executable, SRC_DIR / "ingestion" / "extract_text.py"])
    # 2) Limpieza
    run([sys.executable, SRC_DIR / "ingestion" / "clean_text.py"])
    # 3) Chunking por secciones
    run([sys.executable, SRC_DIR / "ingestion" / "chunk_text_section.py"])
    # 4) Generación de embeddings
    run([sys.executable, SRC_DIR / "embeddings" / "embedder.py"])
    # 5) Subida a Qdrant
    run([sys.executable, SRC_DIR / "vector_store" / "qdrant_uploader.py"])

    print("✅ Índice construido con éxito.")

if __name__ == "__main__":
    main()
