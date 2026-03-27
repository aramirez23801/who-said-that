import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    total_rounds: Mapped[int] = mapped_column(Integer, default=5)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("game_sessions.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"))
    correct_person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", name="fk_round_correct_person")
    )
    wrong_person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", name="fk_round_wrong_person")
    )
    user_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("persons.id", name="fk_round_user_answer"), nullable=True
    )
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
