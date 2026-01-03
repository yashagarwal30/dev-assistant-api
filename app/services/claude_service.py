"""Service for interacting with Claude API."""

import hashlib
from typing import Optional, List, Dict, Any
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.models.conversation import Cache


class ClaudeService:
    """Service for Claude API interactions with caching."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_model = settings.default_model

    @staticmethod
    def _generate_cache_key(prompt: str, model: str, temperature: float) -> str:
        """Generate a unique cache key for a prompt."""
        key_string = f"{prompt}:{model}:{temperature}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def _check_cache(
        self, db: AsyncSession, cache_key: str
    ) -> Optional[Cache]:
        """Check if response exists in cache."""
        result = await db.execute(
            select(Cache).where(Cache.cache_key == cache_key)
        )
        cache_entry = result.scalar_one_or_none()

        if cache_entry:
            # Update hit count and last accessed time
            await db.execute(
                update(Cache)
                .where(Cache.cache_key == cache_key)
                .values(hit_count=Cache.hit_count + 1)
            )
            await db.commit()

        return cache_entry

    async def _save_to_cache(
        self,
        db: AsyncSession,
        cache_key: str,
        prompt: str,
        response: str,
        model: str,
        tokens_used: int,
    ):
        """Save response to cache."""
        cache_entry = Cache(
            cache_key=cache_key,
            prompt=prompt,
            response=response,
            model=model,
            tokens_used=tokens_used,
        )
        db.add(cache_entry)
        await db.commit()

    async def chat(
        self,
        db: AsyncSession,
        message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a chat message to Claude API.

        Args:
            db: Database session
            message: User message
            context: Additional context (e.g., code snippets)
            conversation_history: List of previous messages [{"role": "user", "content": "..."}]
            model: Model to use (default: settings.default_model)
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            use_cache: Whether to use caching

        Returns:
            Dict with response, model, tokens_used, and cached flag
        """
        model = model or self.default_model

        # Build the prompt
        if context:
            full_message = f"Context:\n{context}\n\nQuestion:\n{message}"
        else:
            full_message = message

        # Check cache
        cached = False
        if use_cache:
            cache_key = self._generate_cache_key(full_message, model, temperature)
            cache_entry = await self._check_cache(db, cache_key)
            if cache_entry:
                return {
                    "response": cache_entry.response,
                    "model": cache_entry.model,
                    "tokens_used": cache_entry.tokens_used,
                    "cached": True,
                }

        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": full_message})

        # Call Claude API
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )

        response_text = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        # Save to cache
        if use_cache:
            await self._save_to_cache(
                db, cache_key, full_message, response_text, model, tokens_used
            )

        return {
            "response": response_text,
            "model": model,
            "tokens_used": tokens_used,
            "cached": cached,
        }

    async def analyze_code(
        self,
        db: AsyncSession,
        code: str,
        analysis_type: str,
        file_path: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze code using Claude API.

        Args:
            db: Database session
            code: Code to analyze
            analysis_type: Type of analysis ('review', 'refactor', 'explain', 'optimize', 'test')
            file_path: Optional file path for context
            context: Additional context

        Returns:
            Dict with analysis result and metadata
        """
        prompts = {
            "review": f"Review the following code and provide detailed feedback on:\n"
            f"1. Code quality and best practices\n"
            f"2. Potential bugs or issues\n"
            f"3. Security concerns\n"
            f"4. Performance improvements\n\n"
            f"{'File: ' + file_path if file_path else ''}\n\n```\n{code}\n```",
            "refactor": f"Suggest refactoring improvements for the following code:\n\n"
            f"{'File: ' + file_path if file_path else ''}\n\n```\n{code}\n```",
            "explain": f"Explain what the following code does in detail:\n\n"
            f"{'File: ' + file_path if file_path else ''}\n\n```\n{code}\n```",
            "optimize": f"Suggest optimizations for the following code:\n\n"
            f"{'File: ' + file_path if file_path else ''}\n\n```\n{code}\n```",
            "test": f"Generate unit tests for the following code:\n\n"
            f"{'File: ' + file_path if file_path else ''}\n\n```\n{code}\n```",
        }

        prompt = prompts.get(analysis_type, prompts["review"])
        if context:
            prompt = f"{context}\n\n{prompt}"

        result = await self.chat(
            db=db,
            message=prompt,
            temperature=0.3,  # Lower temperature for code analysis
            max_tokens=4096,
        )

        return result


# Global instance
claude_service = ClaudeService()
