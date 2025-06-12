import uuid
import ollama
from pinecone import Pinecone, ServerlessSpec


class EmbeddingController:
    def __init__(self, model_name="nomic-embed-text", pinecone_api_key="", pinecone_index=""):
        self.model_name = model_name

        pinecone_api_key = str(pinecone_api_key).strip('"\' ')  # Remove any surrounding quotes/whitespace
        pinecone_index = str(pinecone_index).strip('"\'').strip()  # Remove any surrounding quotes and whitespace
        
        if not pinecone_api_key:
            raise ValueError("Pinecone API key is required")
        if not pinecone_index:
            raise ValueError("Pinecone index name is required")
        
        try:
            self.pc = Pinecone(api_key=pinecone_api_key)
            print("Successfully connected to Pinecone")
            
            if pinecone_index not in self.pc.list_indexes().names():
                print(f"Creating new index: {pinecone_index}")
                self.pc.create_index(
                    name=pinecone_index,
                    dimension=768,  # Dimension for nomic-embed-text
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                import time
                time.sleep(1)
            
            self.index = self.pc.Index(pinecone_index)
            print(f"Connected to index: {pinecone_index}")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {str(e)}")
            raise

    def generate_embeddings(self, words):
        try:
            response = ollama.embed(model=self.model_name, input=words)
            return response["embeddings"][0]
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    def store_embeddings(self, embeddings, chunks, chunk_metadata=None):
        try:
            vectors_to_upsert = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                vector_data = {
                    'id': str(uuid.uuid4()),
                    'values': embedding,
                    'metadata': {
                        'text': chunk,
                        **({} if chunk_metadata is None else chunk_metadata[i])
                    }
                }
                vectors_to_upsert.append(vector_data)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
                
        except Exception as e:
            print(f"Error storing embeddings: {str(e)}")
            raise

    def load_and_query_pinecone(self, query_embedding: list, top_k: int = 5): 
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return results