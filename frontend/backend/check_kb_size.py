#!/usr/bin/env python3
import asyncio
import os
import sys
sys.path.append('/home/ec2-user/privategpt/backend')
from app.services.vector_service import vector_service

async def check_kb_stats():
    stats = await vector_service.get_index_stats()
    print("Knowledge Base Statistics:")
    print("=" * 50)
    print(f"Total vectors stored: {stats.get('total_vector_count', 0)}")
    print(f"Index dimension: {stats.get('dimension', 0)}")
    print(f"Index fullness: {stats.get('index_fullness', 0):.2%}")
    
    # Each vector represents a chunk of text
    # Assuming average chunk size of ~500 tokens
    total_vectors = stats.get('total_vector_count', 0)
    estimated_tokens = total_vectors * 500
    estimated_words = estimated_tokens * 0.75  # rough conversion
    
    print(f"\nEstimated content size:")
    print(f"  ~{estimated_tokens:,} tokens")
    print(f"  ~{estimated_words:,.0f} words")
    print(f"  ~{estimated_words/250:.0f} pages (assuming 250 words/page)")
    
    # Also show namespaces if any
    namespaces = stats.get('namespaces', {})
    if namespaces:
        print(f"\nNamespaces:")
        for ns_name, ns_stats in namespaces.items():
            print(f"  {ns_name}: {ns_stats.get('vector_count', 0)} vectors")

if __name__ == "__main__":
    asyncio.run(check_kb_stats())
