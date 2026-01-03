"""Code analysis API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.schemas.conversation import CodeAnalysisRequest, CodeAnalysisResponse
from app.models.conversation import CodeAnalysis
from app.services.claude_service import claude_service

router = APIRouter(prefix="/code", tags=["code-analysis"])


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze code using Claude AI.

    Supported analysis types:
    - review: Comprehensive code review
    - refactor: Refactoring suggestions
    - explain: Code explanation
    - optimize: Performance optimization suggestions
    - test: Generate unit tests
    """
    # Call Claude API for code analysis
    result = await claude_service.analyze_code(
        db=db,
        code=request.code,
        analysis_type=request.analysis_type,
        file_path=request.file_path,
        context=request.context,
    )

    # Save analysis to database
    analysis = CodeAnalysis(
        file_path=request.file_path or "inline_code",
        code_snippet=request.code[:1000],  # Store first 1000 chars
        analysis_type=request.analysis_type,
        result=result["response"],
        model=result["model"],
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return analysis


@router.get("/analysis/history", response_model=List[CodeAnalysisResponse])
async def get_analysis_history(
    analysis_type: str = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Get code analysis history with optional filtering.

    Args:
        analysis_type: Filter by analysis type (review, refactor, etc.)
        limit: Number of results to return
        offset: Number of results to skip
    """
    query = select(CodeAnalysis).order_by(CodeAnalysis.created_at.desc())

    if analysis_type:
        query = query.where(CodeAnalysis.analysis_type == analysis_type)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    analyses = result.scalars().all()

    return analyses


@router.get("/analysis/{analysis_id}", response_model=CodeAnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific code analysis by ID."""
    result = await db.execute(
        select(CodeAnalysis).where(CodeAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis


@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a code analysis."""
    result = await db.execute(
        select(CodeAnalysis).where(CodeAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.delete(analysis)
    await db.commit()

    return {"message": "Analysis deleted successfully"}
