import uuid

from sqlmodel import Field, SQLModel

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
    frame_count: int = Field(nullable=False)
    image: str = Field(nullable=False)
