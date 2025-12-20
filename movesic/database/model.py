from dataclasses import dataclass
from datetime import datetime
import enum
import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship

Base = declarative_base()


class SERVICETYPE_ENUM(enum.Enum):
    YOUTUBE_MUSIC = 1
    SPOTIFY = 2


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    type: Mapped[SERVICETYPE_ENUM] = mapped_column(
        sa.Enum(SERVICETYPE_ENUM), nullable=False
    )
    date_created: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    data: Mapped[dict] = mapped_column(sa.JSON, nullable=False)

    credentials: Mapped[t.List["Credentials"]] = relationship(
        back_populates="app",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


@dataclass
class Credentials(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    app_id: Mapped[int] = mapped_column(
        sa.ForeignKey("applications.id"), nullable=False
    )
    app = relationship("Application")
    date_created: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    data: Mapped[dict] = mapped_column(sa.JSON, nullable=False)

    def __hash__(self):
        return self.id
