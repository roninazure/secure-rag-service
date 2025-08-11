from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: Optional[int] = None
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
