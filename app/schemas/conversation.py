"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Message Schemas
class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    pass


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: int
    conversation_id: int
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = Field(None, max_length=500)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    session_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


# Chat Schemas
class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    context: Optional[str] = Field(None, description="Additional context like code snippets")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(4096, ge=1, le=8192)


class ChatResponse(BaseModel):
    """Schema for chat response."""
    session_id: str
    message: str
    model: str
    tokens_used: int
    cached: bool = False


# Code Analysis Schemas
class CodeAnalysisRequest(BaseModel):
    """Schema for code analysis request."""
    code: str = Field(..., min_length=1)
    file_path: Optional[str] = Field(None, max_length=1000)
    analysis_type: str = Field(..., pattern="^(review|refactor|explain|optimize|test)$")
    context: Optional[str] = None


class CodeAnalysisResponse(BaseModel):
    """Schema for code analysis response."""
    id: int
    analysis_type: str
    result: str
    confidence_score: Optional[float] = None
    model: str
    created_at: datetime

    class Config:
        from_attributes = True


# Cache Schemas
class CacheStats(BaseModel):
    """Schema for cache statistics."""
    total_entries: int
    total_hits: int
    cache_size_mb: float
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
