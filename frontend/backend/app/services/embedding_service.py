import os
import asyncio
import boto3
import json
from typing import List, Optional
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.embedding_model_id = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2")
        
        self.test_mode = not all([self.aws_access_key_id, self.aws_secret_access_key])
        
        if not self.test_mode:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            self.bedrock_client = None
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Titan Embeddings"""
        if self.test_mode:
            # Return mock embeddings for testing
            return [[0.1] * 1024 for _ in texts]  # Titan v2 uses 1024 dimensions
        
        embeddings = []
        
        for text in texts:
            try:
                body = json.dumps({
                    "inputText": text
                })
                
                response = await asyncio.to_thread(
                    self.bedrock_client.invoke_model,
                    modelId=self.embedding_model_id,
                    body=body,
                    accept='application/json',
                    contentType='application/json'
                )
                
                response_body = json.loads(response.get('body').read())
                embedding = response_body.get('embedding', [])
                embeddings.append(embedding)
                
            except ClientError as e:
                print(f"Bedrock Embedding Error: {e}")
                # Return zero vector on error
                embeddings.append([0.0] * 1024)
            except Exception as e:
                print(f"Embedding generation error: {e}")
                embeddings.append([0.0] * 1024)
        
        return embeddings
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * 1024

# Global instance
embedding_service = EmbeddingService()
