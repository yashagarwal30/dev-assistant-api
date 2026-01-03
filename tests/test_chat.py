"""Tests for chat endpoints."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint():
    """Test basic chat functionality."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/",
            json={
                "message": "Hello, what is FastAPI?",
                "temperature": 0.7,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert "model" in data
        assert "tokens_used" in data


@pytest.mark.asyncio
async def test_chat_with_context():
    """Test chat with code context."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/",
            json={
                "message": "Explain this code",
                "context": "def hello():\n    print('Hello, World!')",
                "temperature": 0.5,
            },
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_conversation_continuity():
    """Test conversation continuation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First message
        response1 = await client.post(
            "/chat/",
            json={"message": "My name is Alice"},
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]

        # Second message in same conversation
        response2 = await client.post(
            "/chat/",
            json={
                "message": "What is my name?",
                "session_id": session_id,
            },
        )
        assert response2.status_code == 200
        assert session_id == response2.json()["session_id"]
