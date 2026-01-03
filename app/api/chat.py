"""Chat API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationCreate,
)
from app.models.conversation import Conversation, Message
from app.services.claude_service import claude_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message and get AI response.

    - Creates a new conversation if session_id is not provided
    - Continues existing conversation if session_id is provided
    - Supports code context for better assistance
    """
    # Get or create conversation
    if request.session_id:
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == request.session_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(session_id=str(uuid.uuid4()))
        db.add(conversation)
        await db.flush()

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history_messages = result.scalars().all()

    # Build conversation history for Claude
    conversation_history = [
        {"role": msg.role, "content": msg.content} for msg in history_messages
    ]

    # Call Claude API
    response_data = await claude_service.chat(
        db=db,
        message=request.message,
        context=request.context,
        conversation_history=conversation_history,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_message)

    # Save assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_data["response"],
        model=response_data["model"],
        tokens_used=response_data["tokens_used"],
    )
    db.add(assistant_message)

    await db.commit()

    return ChatResponse(
        session_id=conversation.session_id,
        message=response_data["response"],
        model=response_data["model"],
        tokens_used=response_data["tokens_used"],
        cached=response_data["cached"],
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all conversations with pagination."""
    result = await db.execute(
        select(Conversation)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/conversations/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation with all messages."""
    result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.delete("/conversations/{session_id}")
async def delete_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()

    return {"message": "Conversation deleted successfully"}
