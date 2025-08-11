from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
import datetime
from typing import Dict, List

router = APIRouter()

# Store conversation history in memory (for testing)
# In production, use Redis or database
conversation_history: Dict[str, List[Dict]] = {}


@router.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message and return RAG-enhanced AI response"""
    try:
        # Get or create conversation history for this session
        # Using a default session ID for now - in production, use actual session management
        session_id = "default_session"
        
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add user message to history
        conversation_history[session_id].append({
            "role": "user",
            "content": request.message
        })
        
        # Build context-aware message including recent history
        context_message = request.message
        if len(conversation_history[session_id]) > 1:
            # Include last 2 exchanges (4 messages) for context
            recent_history = conversation_history[session_id][-5:-1]  # Exclude current message
            if recent_history:
                history_text = "\n".join([
                    f"{msg['role'].capitalize()}: {msg['content']}" 
                    for msg in recent_history
                ])
                # Format context more naturally without explicit labels
                context_message = f"""Previous conversation:
{history_text}

User: {request.message}"""
        
        # Use RAG service with context-aware message
        rag_result = await rag_service.query_with_rag(context_message)
        
        # Add AI response to history
        conversation_history[session_id].append({
            "role": "assistant",
            "content": rag_result["response"]
        })
        
        # Keep conversation history limited to last 10 exchanges
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        id = int(datetime.datetime.now().timestamp())
        response = ChatResponse(
            id=id,
            role="assistant",
            content=rag_result["response"],
            timestamp=datetime.datetime.now()
        )
        return response
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        # Fallback response
        id = int(datetime.datetime.now().timestamp())
        response = ChatResponse(
            id=id,
            role="assistant",
            content="I'm experiencing technical difficulties. Please try again later.",
            timestamp=datetime.datetime.now()
        )
        return response
