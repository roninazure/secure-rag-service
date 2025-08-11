import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

class VectorService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "privategpt-embeddings")
        self.host = os.getenv("PINECONE_HOST")
        
        self.test_mode = not self.api_key
        
        if not self.test_mode:
            self.pc = Pinecone(api_key=self.api_key)
            self.index = None
            self._connect_to_index()
        else:
            self.pc = None
            self.index = None
    
    def _connect_to_index(self):
        """Connect to existing Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                self.index = self.pc.Index(self.index_name)
                print(f"Connected to existing Pinecone index: {self.index_name}")
            else:
                print(f"Index {self.index_name} not found. Available indexes: {existing_indexes}")
                # Create index if it doesn't exist
                self._create_index()
                
        except Exception as e:
            print(f"Error connecting to Pinecone: {e}")
    
    def _create_index(self):
        """Create a new Pinecone index"""
        try:
            self.pc.create_index(
                name=self.index_name,
                dimension=1024,  # Titan v2 embedding dimensions
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.environment
                )
            )
            self.index = self.pc.Index(self.index_name)
            print(f"Created new Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"Error creating Pinecone index: {e}")
    
    async def store_documents(self, texts: List[str], embeddings: List[List[float]], 
                            metadata: List[Dict[str, Any]] = None) -> List[str]:
        """Store document embeddings in Pinecone"""
        if self.test_mode or not self.index:
            return [f"test-id-{i}" for i in range(len(texts))]
        
        try:
            # Generate IDs for the documents
            doc_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # Prepare vectors for upsert
            vectors = []
            for i, (doc_id, embedding, text) in enumerate(zip(doc_ids, embeddings, texts)):
                vector_data = {
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {
                        "text": text[:1000],  # Truncate text for metadata
                        "document_type": "user_upload",
                        "timestamp": str(uuid.uuid1().time),
                        **(metadata[i] if metadata and i < len(metadata) else {})
                    }
                }
                vectors.append(vector_data)
            
            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors)
            print(f"Successfully stored {len(vectors)} documents in Pinecone")
            return doc_ids
            
        except Exception as e:
            print(f"Error storing documents in Pinecone: {e}")
            return []
    
    async def search_similar(self, query_embedding: List[float], 
                           top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar documents in Pinecone"""
        if self.test_mode or not self.index:
            # Return mock results for testing
            return [
                ("test-doc-1", 0.9, {"text": "This is a test document for RAG functionality."}),
                ("test-doc-2", 0.8, {"text": "Another test document with relevant information."})
            ]
        
        try:
            # Query Pinecone
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )
            
            # Extract results
            results = []
            for match in response.matches:
                doc_id = match.id
                score = match.score
                metadata = match.metadata
                results.append((doc_id, score, metadata))
            
            print(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.test_mode or not self.index:
            return {"total_vectors": 0, "status": "test_mode"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {"error": str(e)}

# Global instance
vector_service = VectorService()
