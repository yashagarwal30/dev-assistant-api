"""Admin and utility API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.schemas.conversation import CacheStats
from app.models.conversation import Cache, Conversation, Message, CodeAnalysis

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats(db: AsyncSession = Depends(get_db)):
    """Get cache statistics."""
    # Total entries
    total_result = await db.execute(select(func.count(Cache.id)))
    total_entries = total_result.scalar() or 0

    # Total hits
    hits_result = await db.execute(select(func.sum(Cache.hit_count)))
    total_hits = hits_result.scalar() or 0

    # Get oldest and newest entries
    oldest_result = await db.execute(
        select(Cache.created_at).order_by(Cache.created_at).limit(1)
    )
    oldest = oldest_result.scalar_one_or_none()

    newest_result = await db.execute(
        select(Cache.created_at).order_by(Cache.created_at.desc()).limit(1)
    )
    newest = newest_result.scalar_one_or_none()

    return CacheStats(
        total_entries=total_entries,
        total_hits=total_hits,
        cache_size_mb=0.0,  # Calculate if needed
        oldest_entry=oldest,
        newest_entry=newest,
    )


@router.delete("/cache/clear")
async def clear_cache(db: AsyncSession = Depends(get_db)):
    """Clear all cache entries."""
    result = await db.execute(select(Cache))
    caches = result.scalars().all()

    for cache in caches:
        await db.delete(cache)

    await db.commit()

    return {"message": f"Cleared {len(caches)} cache entries"}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get overall API statistics."""
    # Count conversations
    conv_result = await db.execute(select(func.count(Conversation.id)))
    total_conversations = conv_result.scalar() or 0

    # Count messages
    msg_result = await db.execute(select(func.count(Message.id)))
    total_messages = msg_result.scalar() or 0

    # Count code analyses
    analysis_result = await db.execute(select(func.count(CodeAnalysis.id)))
    total_analyses = analysis_result.scalar() or 0

    # Total tokens used
    tokens_result = await db.execute(
        select(func.sum(Message.tokens_used)).where(Message.tokens_used.isnot(None))
    )
    total_tokens = tokens_result.scalar() or 0

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_code_analyses": total_analyses,
        "total_tokens_used": total_tokens,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dev-assistant-api"}
