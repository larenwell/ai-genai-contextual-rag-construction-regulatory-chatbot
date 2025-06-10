# src/embeddings/embedder.py

from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Modelo elegido y tamaño de batch
MODEL_NAME = "intfloat/multilingual-e5-large-instruct"
BATCH_SIZE = 32

def embed_and_serialize(
    chunks_dir: Path,
    embeddings_dir: Path,
    model_name: str = MODEL_NAME,
    batch_size: int = BATCH_SIZE
):
    """
    1) Carga el modelo SentenceTransformer.
    2) Lee todos los chunks (*.txt) de chunks_dir.
    3) Genera embeddings normalizados (L2) en batch.
    4) Escribe UN solo JSON por chunk:
       {
         "id": <chunk_id>,
         "text": <texto completo>,
         "vector": [float, float, …]    # 1024 dims
       }
    """
    # 1) Inicializa el modelo
    model = SentenceTransformer(model_name)

    # 2) Prepara carpeta de salida
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    # 3) Carga todos los chunks
    chunk_files = sorted(chunks_dir.glob("*.txt"))
    ids   = [f.stem for f in chunk_files]
    texts = [f.read_text(encoding="utf-8") for f in chunk_files]

    # 4) Encode en batch
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # 5) Serializa JSON por chunk
    for chunk_id, text, vector in zip(ids, texts, embeddings):
        out = {
            "id":     chunk_id,
            "text":   text,
            "vector": vector.tolist()
        }
        json_path = embeddings_dir / f"{chunk_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        print(f"→ Embedded & saved {chunk_id}.json")

def main():
    project_root  = Path.cwd()
    chunks_dir    = project_root / "data" / "chunks_sections"
    embeddings_dir= project_root / "data" / "embeddings"

    if not chunks_dir.exists() or not any(chunks_dir.iterdir()):
        print(f"No hay chunks en {chunks_dir}")
        return

    embed_and_serialize(chunks_dir, embeddings_dir)

if __name__ == "__main__":
    main()
