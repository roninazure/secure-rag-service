#!/usr/bin/env python3
"""
Reset Pinecone vector database by clearing all vectors
"""

import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

def reset_pinecone():
    """Clear all vectors from Pinecone index"""
    
    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "privategpt")
    
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        return
    
    print("=" * 60)
    print("RESETTING PINECONE VECTOR DATABASE")
    print("=" * 60)
    
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        # Get current stats
        stats = index.describe_index_stats()
        current_vectors = stats.get('total_vector_count', 0)
        print(f"\nCurrent vectors in index: {current_vectors}")
        
        if current_vectors > 0:
            # Delete all vectors
            print("Deleting all vectors...")
            index.delete(delete_all=True)
            print("✅ All vectors deleted")
            
            # Verify deletion
            stats = index.describe_index_stats()
            new_count = stats.get('total_vector_count', 0)
            print(f"Vectors after deletion: {new_count}")
        else:
            print("Index is already empty")
            
        print("\n✅ Vector database reset complete!")
        print("You can now ingest fresh documents.")
        
    except Exception as e:
        print(f"❌ Error resetting Pinecone: {e}")

if __name__ == "__main__":
    reset_pinecone()
