from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
