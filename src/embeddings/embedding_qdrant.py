# Now instead of using Pinecone as the vectorized DB, we will use Qdrant
import os
import uuid
import ollama
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

QDRANT_URL = "http://localhost:6333"  # Default Qdrant URL
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "norms-mistral")

class EmbeddingControllerQdrant:
    def __init__(self, model_name: str = "nomic-embed-text", qdrant_url: str = QDRANT_URL, qdrant_collection: str =  QDRANT_COLLECTION_NAME):
        self.model_name = model_name
        self.qdrant_url = qdrant_url
        self.qdrant_collection = qdrant_collection

        if not self.qdrant_url:
            raise ValueError("Qdrant URL is required")
        if not self.qdrant_collection:
            raise ValueError("Qdrant collection name is required")

        self.qdrant_client = QdrantClient(url=qdrant_url)

        # Check if collection exists, if not create it
        collections = self.qdrant_client.get_collections().collections
        if not any(col.name == self.qdrant_collection for col in collections):
            print(f"Creating new collection: {self.qdrant_collection}")
            self.qdrant_client.create_collection(
                collection_name=self.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=768,  # Dimension for nomic-embed-text
                    distance=models.Distance.COSINE
                )
            )

    def generate_embeddings(self, text: str) -> list:
        try:
            response = ollama.embed(model=self.model_name, input=text)
            return response["embeddings"][0]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
        
    def store_embeddings(self, embeddings: list, chunks: list, chunk_metadata: list = []):
        try:
            points_to_upsert = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                # Extract text content from chunk
                if isinstance(chunk, dict):
                    text_content = chunk.get('content', str(chunk))
                    # Extract metadata from chunk, excluding the content field
                    chunk_meta = {k: v for k, v in chunk.get('metadata', {}).items() 
                                if k != 'content' and isinstance(v, (str, int, float, bool, list))}
                else:
                    text_content = str(chunk)
                    chunk_meta = {}
                
                # Combine metadata
                metadata = {
                    'text': text_content,
                    **chunk_meta,
                    **({} if chunk_metadata is None else chunk_metadata[i])
                }
                
                point = models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=metadata
                )
                points_to_upsert.append(point)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points_to_upsert), batch_size):
                batch = points_to_upsert[i:i + batch_size]
                self.qdrant_client.upsert(
                    collection_name=self.qdrant_collection,
                    points=batch
                )
                print(f"Upserted batch {i//batch_size + 1}/{(len(points_to_upsert)-1)//batch_size + 1}")
                
        except Exception as e:
            print(f"Error storing embeddings: {str(e)}")
            raise
        

    def load_and_query_qdrant(self, query_embedding: list, top_k: int = 4):
        results = self.qdrant_client.search(
            collection_name=self.qdrant_collection,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return results


        