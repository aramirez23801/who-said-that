from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    image_url: Mapped[str] = mapped_column(Text)
    short_bio: Mapped[str] = mapped_column(String(200))
