import uuid

from sqlmodel import Field, Relationship, SQLModel

from models.file import File

from .mixins import TimestampMixin


class Frame(TimestampMixin, SQLModel, table=True):
    __tablename__ = "frame"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    file_id: uuid.UUID = Field(foreign_key="file.id", nullable=False)
    file: File = Relationship(back_populates="frame")
    frame_count: int = Field(nullable=False)
    image: str = Field(nullable=False)
