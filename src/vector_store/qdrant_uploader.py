# src/vector_store/qdrant_uploader.py

from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
import json

QDRANT_HOST     = "localhost"
QDRANT_PORT     = 6333
COLLECTION_NAME = "normativa"

def init_qdrant():
    client = QdrantClient(url=f"http://{QDRANT_HOST}:{QDRANT_PORT}")
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance="Cosine")
        )
    return client

def upload_from_json(embeddings_dir: Path):
    client = init_qdrant()
    json_files = sorted(embeddings_dir.glob("*.json"))

    batch = []
    for idx, jpath in enumerate(json_files, start=1):
        data = json.loads(jpath.read_text(encoding="utf-8"))
        # id numérico válido para Qdrant
        point_id = idx
        batch.append(
            PointStruct(
                id      = point_id,
                vector  = data["vector"],
                payload = {
                    "chunk_key": data["id"],
                    "text":      data["text"]
                }
            )
        )
        if len(batch) >= 64:
            client.upsert(COLLECTION_NAME, batch)
            batch.clear()

    if batch:
        client.upsert(COLLECTION_NAME, batch)

    print(f"✅ Subidos {len(json_files)} vectores a Qdrant.")

if __name__ == "__main__":
    root = Path.cwd()
    upload_from_json(root/"data"/"embeddings")
