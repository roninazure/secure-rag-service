import os
from typing import List, Dict, Any, Tuple
import re

class ChunkingService:
    def __init__(self):
        # Chunking configuration - smaller chunks for better precision
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "300"))  # Smaller chunks for better precision
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))  # Smaller overlap
        self.max_chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "600"))  # Maximum chunk size
        self.min_chunk_size = int(os.getenv("MIN_CHUNK_SIZE", "100"))  # Minimum chunk size
        
        # Sentence splitting pattern
        self.sentence_endings = re.compile(r'[.!?]\s+')
        
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into chunks with overlap, preserving sentence boundaries
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of tuples containing (chunk_text, chunk_metadata)
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Clean the text
        text = text.strip()
        
        # If text is small enough, return as single chunk
        if len(text) <= self.chunk_size:
            chunk_metadata = self._create_chunk_metadata(
                original_metadata=metadata,
                chunk_index=0,
                total_chunks=1,
                char_start=0,
                char_end=len(text)
            )
            return [(text, chunk_metadata)]
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        # Create chunks with overlap
        chunks = self._create_chunks_with_overlap(sentences, text)
        
        # Add metadata to each chunk
        chunks_with_metadata = []
        total_chunks = len(chunks)
        
        for idx, (chunk_text, char_start, char_end) in enumerate(chunks):
            chunk_metadata = self._create_chunk_metadata(
                original_metadata=metadata,
                chunk_index=idx,
                total_chunks=total_chunks,
                char_start=char_start,
                char_end=char_end
            )
            chunks_with_metadata.append((chunk_text, chunk_metadata))
        
        return chunks_with_metadata
    
    def chunk_documents(self, documents: List[str], metadata_list: List[Dict[str, Any]] = None) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Chunk multiple documents with overlap
        
        Args:
            documents: List of documents to chunk
            metadata_list: Optional list of metadata for each document
            
        Returns:
            Tuple of (chunked_texts, chunked_metadata)
        """
        if metadata_list is None:
            metadata_list = [{}] * len(documents)
        
        all_chunks = []
        all_metadata = []
        
        for doc_idx, (doc, metadata) in enumerate(zip(documents, metadata_list)):
            # Add document index to metadata
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata['source_document_index'] = doc_idx
            
            # Chunk the document
            chunks_with_metadata = self.chunk_text(doc, doc_metadata)
            
            # Collect chunks and metadata
            for chunk_text, chunk_metadata in chunks_with_metadata:
                all_chunks.append(chunk_text)
                all_metadata.append(chunk_metadata)
        
        return all_chunks, all_metadata
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Use regex to split by sentence endings
        sentences = []
        current_pos = 0
        
        for match in self.sentence_endings.finditer(text):
            end_pos = match.end()
            sentence = text[current_pos:end_pos].strip()
            if sentence:
                sentences.append(sentence)
            current_pos = end_pos
        
        # Add any remaining text
        if current_pos < len(text):
            remaining = text[current_pos:].strip()
            if remaining:
                sentences.append(remaining)
        
        # If no sentences found, split by paragraphs
        if not sentences:
            sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # If still no splits, split by lines
        if not sentences:
            sentences = [l.strip() for l in text.split('\n') if l.strip()]
        
        # If still nothing, return the whole text
        if not sentences:
            sentences = [text]
        
        return sentences
    
    def _create_chunks_with_overlap(self, sentences: List[str], original_text: str) -> List[Tuple[str, int, int]]:
        """
        Create chunks from sentences with overlap
        
        Returns:
            List of tuples (chunk_text, char_start, char_end)
        """
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        
        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_chunk_size + sentence_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                char_start = original_text.find(current_chunk[0])
                char_end = char_start + len(chunk_text)
                chunks.append((chunk_text, char_start, char_end))
                
                # Calculate overlap - keep last sentences that fit in overlap size
                overlap_chunk = []
                overlap_size = 0
                
                for sent in reversed(current_chunk):
                    sent_size = len(sent)
                    if overlap_size + sent_size <= self.chunk_overlap:
                        overlap_chunk.insert(0, sent)
                        overlap_size += sent_size
                    else:
                        break
                
                # Start new chunk with overlap
                current_chunk = overlap_chunk
                current_chunk_size = overlap_size
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_chunk_size += sentence_size
            
            # If chunk exceeds max size, force a split
            if current_chunk_size > self.max_chunk_size:
                chunk_text = ' '.join(current_chunk[:-1]) if len(current_chunk) > 1 else current_chunk[0]
                char_start = original_text.find(current_chunk[0])
                char_end = char_start + len(chunk_text)
                chunks.append((chunk_text, char_start, char_end))
                
                # Start new chunk with the last sentence
                current_chunk = [sentence]
                current_chunk_size = sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            char_start = original_text.find(current_chunk[0])
            char_end = char_start + len(chunk_text)
            chunks.append((chunk_text, char_start, char_end))
        
        return chunks
    
    def _create_chunk_metadata(self, original_metadata: Dict[str, Any], 
                              chunk_index: int, total_chunks: int,
                              char_start: int, char_end: int) -> Dict[str, Any]:
        """Create metadata for a chunk"""
        chunk_metadata = original_metadata.copy() if original_metadata else {}
        
        # Add chunking information
        chunk_metadata.update({
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'char_start': char_start,
            'char_end': char_end,
            'chunk_id': f"chunk_{chunk_index}_of_{total_chunks}"
        })
        
        return chunk_metadata
    
    def estimate_chunks(self, text: str) -> int:
        """Estimate the number of chunks for a given text"""
        if not text:
            return 0
        
        text_length = len(text)
        
        if text_length <= self.chunk_size:
            return 1
        
        # Account for overlap
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        estimated_chunks = (text_length - self.chunk_size) // effective_chunk_size + 1
        
        return max(1, estimated_chunks)

# Global instance
chunking_service = ChunkingService()
