#!/usr/bin/env python3
"""
Test script for document chunking functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.chunking_service import chunking_service

def test_chunking():
    """Test the chunking service with various document sizes"""
    
    print("=" * 60)
    print("Testing Document Chunking Service")
    print("=" * 60)
    
    # Test 1: Small document (should not be chunked)
    small_doc = "This is a small document that should not be chunked."
    print("\n1. Testing small document:")
    print(f"   Original length: {len(small_doc)} chars")
    
    chunks = chunking_service.chunk_text(small_doc)
    print(f"   Number of chunks: {len(chunks)}")
    for i, (chunk, metadata) in enumerate(chunks):
        print(f"   Chunk {i}: {len(chunk)} chars")
        print(f"   Metadata: {metadata}")
    
    # Test 2: Medium document (should be chunked into 2-3 chunks)
    medium_doc = """
    Remote Work Policy

    Effective Date: January 1, 2024
    
    1. ELIGIBILITY
    All full-time employees who have completed their probationary period of 90 days are eligible to request remote work arrangements. Eligibility is subject to the nature of the role, performance history, and manager approval. Employees must maintain a satisfactory performance rating to continue remote work privileges.
    
    2. APPLICATION PROCESS
    Employees interested in remote work must submit a formal request through the HR portal at least 30 days before the desired start date. The request must include a detailed remote work plan, including proposed schedule, communication protocols, and workspace setup. All requests require approval from the direct manager and Dan Pfeiffer, VP of Human Resources.
    
    3. EQUIPMENT AND WORKSPACE
    The company will provide necessary equipment including laptop, monitor, and ergonomic accessories up to a value of $1,500. Employees are responsible for maintaining a professional, quiet, and secure workspace. Internet connectivity of at least 50 Mbps is required for video conferencing. The company will reimburse up to $50 monthly for internet expenses upon receipt submission.
    
    4. WORK HOURS AND AVAILABILITY
    Remote employees must maintain core hours from 10 AM to 3 PM in their local time zone for meetings and collaboration. Total work hours should align with standard company policy of 40 hours per week. Employees must be available via company communication tools during work hours and respond to messages within 2 hours during core hours.
    
    5. PERFORMANCE EXPECTATIONS
    Remote employees are held to the same performance standards as in-office employees. Regular check-ins with managers will occur weekly via video conference. Quarterly performance reviews will assess productivity, communication, and collaboration effectiveness. Failure to meet performance standards may result in revocation of remote work privileges.
    """
    
    print("\n2. Testing medium document:")
    print(f"   Original length: {len(medium_doc)} chars")
    
    chunks = chunking_service.chunk_text(medium_doc)
    print(f"   Number of chunks: {len(chunks)}")
    for i, (chunk, metadata) in enumerate(chunks):
        print(f"\n   Chunk {i}:")
        print(f"   - Length: {len(chunk)} chars")
        print(f"   - Metadata: chunk_id={metadata.get('chunk_id')}, "
              f"chars={metadata.get('char_start')}-{metadata.get('char_end')}")
        print(f"   - Preview: {chunk[:100]}...")
    
    # Test 3: Test chunking with overlap
    print("\n3. Testing overlap between chunks:")
    if len(chunks) > 1:
        for i in range(len(chunks) - 1):
            chunk1_text = chunks[i][0]
            chunk2_text = chunks[i + 1][0]
            
            # Find potential overlap
            overlap_size = 0
            for j in range(min(200, len(chunk1_text), len(chunk2_text))):
                end_of_chunk1 = chunk1_text[-(j+1):]
                start_of_chunk2 = chunk2_text[:j+1]
                if end_of_chunk1 in chunk2_text[:400]:  # Check if end of chunk1 appears in start of chunk2
                    overlap_size = max(overlap_size, j+1)
            
            print(f"   Chunks {i} and {i+1}: ~{overlap_size} chars overlap detected")
    
    # Test 4: Test with documents list
    print("\n4. Testing multiple documents:")
    docs = [
        "First document about company policies.",
        "Second document with different content about procedures and guidelines for employees.",
        medium_doc  # Reuse the medium document
    ]
    
    all_chunks, all_metadata = chunking_service.chunk_documents(docs)
    print(f"   Total documents: {len(docs)}")
    print(f"   Total chunks created: {len(all_chunks)}")
    
    # Group chunks by source document
    doc_chunks = {}
    for chunk, metadata in zip(all_chunks, all_metadata):
        doc_idx = metadata.get('source_document_index', -1)
        if doc_idx not in doc_chunks:
            doc_chunks[doc_idx] = []
        doc_chunks[doc_idx].append((chunk, metadata))
    
    for doc_idx, chunks in doc_chunks.items():
        print(f"   Document {doc_idx}: {len(chunks)} chunks")
    
    # Test 5: Estimate chunks
    print("\n5. Testing chunk estimation:")
    test_sizes = [100, 500, 1000, 2000, 5000]
    for size in test_sizes:
        test_text = "x" * size
        estimated = chunking_service.estimate_chunks(test_text)
        actual_chunks = chunking_service.chunk_text(test_text)
        print(f"   {size} chars: estimated {estimated} chunks, actual {len(actual_chunks)} chunks")
    
    print("\n" + "=" * 60)
    print("Chunking Configuration:")
    print(f"  Chunk size: {chunking_service.chunk_size} chars")
    print(f"  Overlap: {chunking_service.chunk_overlap} chars")
    print(f"  Max chunk: {chunking_service.max_chunk_size} chars")
    print(f"  Min chunk: {chunking_service.min_chunk_size} chars")
    print("=" * 60)

if __name__ == "__main__":
    test_chunking()
