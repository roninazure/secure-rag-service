import os
from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service
from app.services.ai_service import ai_service
from app.services.chunking_service import chunking_service

class RAGService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.ai_service = ai_service
        
        # RAG Configuration
        self.max_context_length = int(os.getenv("RAG_MAX_CONTEXT_LENGTH", "4000"))
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.3"))  # Lowered for better recall
        self.top_k_results = int(os.getenv("RAG_TOP_K", "7"))  # Increased to get more context
    
    async def ingest_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest documents into the RAG system with intelligent chunking"""
        try:
            # Chunk documents with overlap for better context preservation
            chunked_texts, chunked_metadata = chunking_service.chunk_documents(
                documents=documents,
                metadata_list=metadata
            )
            
            # Log chunking information
            original_count = len(documents)
            chunk_count = len(chunked_texts)
            print(f"Chunked {original_count} documents into {chunk_count} chunks")
            
            # Generate embeddings for chunks
            embeddings = await self.embedding_service.generate_embeddings(chunked_texts)
            
            # Store chunks in vector database
            doc_ids = await self.vector_service.store_documents(
                texts=chunked_texts,
                embeddings=embeddings,
                metadata=chunked_metadata
            )
            
            return {
                "success": True,
                "document_count": original_count,
                "chunk_count": chunk_count,
                "doc_ids": doc_ids,
                "message": f"Successfully ingested {original_count} documents as {chunk_count} chunks"
            }
            
        except Exception as e:
            print(f"Document ingestion error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to ingest documents"
            }
    
    async def query_with_rag(self, question: str, use_rag: bool = True) -> Dict[str, Any]:
        """Query the RAG system with context retrieval"""
        try:
            context_documents = []
            context_info = {"used_rag": False, "sources": []}
            
            if use_rag:
                # Generate embedding for the question
                query_embedding = await self.embedding_service.generate_single_embedding(question)
                
                # Search for relevant documents
                search_results = await self.vector_service.search_similar(
                    query_embedding=query_embedding,
                    top_k=self.top_k_results
                )
                
                # Filter by similarity threshold and extract context
                print(f"\n[RAG Debug] Query: {question[:50]}...")
                print(f"[RAG Debug] Found {len(search_results)} results")
                
                for doc_id, score, metadata in search_results:
                    text_preview = metadata.get("text", "")[:100]
                    print(f"[RAG Debug] Score: {score:.3f} - Text: {text_preview}...")
                    
                    if score >= self.similarity_threshold:
                        context_documents.append(metadata.get("text", ""))
                        context_info["sources"].append({
                            "doc_id": doc_id,
                            "similarity": score,
                            "chunk_info": {
                                "chunk_id": metadata.get("chunk_id", "unknown"),
                                "chunk_index": metadata.get("chunk_index", 0),
                                "total_chunks": metadata.get("total_chunks", 1)
                            },
                            "preview": metadata.get("text", "")[:100] + "..."
                        })
                
                print(f"[RAG Debug] Using {len(context_documents)} documents above threshold {self.similarity_threshold}")
                
                context_info["used_rag"] = len(context_documents) > 0
            
            # Build enhanced question with context directly embedded
            enhanced_question = self._build_enhanced_question(context_documents, question)
            
            # Generate AI response with context
            system_prompt = self._build_system_prompt()
            ai_response = await self.ai_service.generate_response(
                message=enhanced_question,
                system_prompt=system_prompt
            )
            
            return {
                "response": ai_response,
                "context_info": context_info,
                "question": question
            }
            
        except Exception as e:
            print(f"RAG query error: {e}")
            return {
                "response": f"I encountered an error processing your question: {str(e)}",
                "context_info": {"used_rag": False, "sources": [], "error": str(e)},
                "question": question
            }
    
    def _build_context(self, context_documents: List[str], question: str) -> str:
        """Build context string from retrieved documents"""
        if not context_documents:
            return ""
        
        # Combine and truncate context to fit within limits
        combined_context = "\n\n".join(context_documents)
        
        if len(combined_context) > self.max_context_length:
            combined_context = combined_context[:self.max_context_length] + "..."
        
        return combined_context
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the AI assistant"""
        return """You are an AI assistant for a law firm's Private GPT system. 
        You provide helpful, accurate, and professional responses based ONLY on the firm's knowledge base.
        
        CRITICAL INSTRUCTIONS:
        1. Only provide information that is explicitly stated in the provided context
        2. If information is not in the context, say "I don't have that information in my knowledge base"
        3. NEVER make up or invent client names, case details, dates, or any other information
        4. NEVER generate fictional documents, contracts, or correspondence
        5. If asked about something not in the context, be honest about the limitation
        6. Be concise and professional in your responses
        
        Remember: It's better to admit you don't know than to provide incorrect information."""
    
    def _build_enhanced_question(self, context_documents: List[str], question: str) -> str:
        """Build an enhanced question with context embedded directly"""
        if not context_documents:
            return question
        
        # Combine context documents
        context_text = self._build_context(context_documents, question)
        
        # Clean the question to remove any conversation formatting
        clean_question = question
        if "Previous conversation:" in clean_question:
            # Extract just the actual current question
            parts = clean_question.split("\n\nUser: ")
            if len(parts) > 1:
                clean_question = parts[-1].strip()
            else:
                # Try another pattern
                parts = clean_question.split("\nUser: ")
                if len(parts) > 1:
                    clean_question = parts[-1].strip()
        
        # Create enhanced prompt with context directly in the question
        enhanced_prompt = f"""Context from knowledge base:
{context_text}

Based on the context above, please answer this question: {clean_question}

Provide a direct answer using only the information from the context. If the information is not available in the context, say so clearly."""
        
        return enhanced_prompt
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get RAG system status"""
        try:
            # Get vector database stats
            vector_stats = await self.vector_service.get_index_stats()
            
            return {
                "status": "operational",
                "vector_database": vector_stats,
                "embedding_model": self.embedding_service.embedding_model_id,
                "text_generation_model": self.ai_service.model_id,
                "configuration": {
                    "max_context_length": self.max_context_length,
                    "similarity_threshold": self.similarity_threshold,
                    "top_k_results": self.top_k_results,
                    "chunking": {
                        "chunk_size": chunking_service.chunk_size,
                        "chunk_overlap": chunking_service.chunk_overlap,
                        "max_chunk_size": chunking_service.max_chunk_size
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global instance
rag_service = RAGService()
