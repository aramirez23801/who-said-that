from datetime import datetime

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    score: int
    total_rounds: int
    played_at: datetime


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
