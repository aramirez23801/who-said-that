from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.game import GameSession
from backend.models.user import User
from backend.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(
        select(GameSession, User)
        .join(User, GameSession.user_id == User.id)
        .where(GameSession.completed == True)  # noqa: E712
        .order_by(GameSession.score.desc(), GameSession.created_at.asc())
        .limit(limit)
    )).all()

    entries = [
        LeaderboardEntry(
            rank=i,
            username=user.username,
            score=session.score,
            total_rounds=session.total_rounds,
            played_at=session.created_at,
        )
        for i, (session, user) in enumerate(rows, start=1)
    ]

    return LeaderboardResponse(entries=entries)
