import uuid

from sqlmodel import Field, Relationship, SQLModel

from models.file import File

from .mixins import TimestampMixin


class Object(TimestampMixin, SQLModel, table=True):
    __tablename__ = "object"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    frame_id: uuid.UUID = Field(foreign_key="frame.id", nullable=False)
    frame: File = Relationship(back_populates="object")
    label: str = Field(nullable=False, index=True)
    score: float = Field(nullable=False)
