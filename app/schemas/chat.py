from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    message_history: List[Dict[str, Any]] = []
