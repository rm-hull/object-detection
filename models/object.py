import uuid

from sqlmodel import Field, SQLModel

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
    file_id: uuid.UUID = Field(foreign_key="file.id", nullable=False)
    label: str = Field(nullable=False, index=True)
    score: float = Field(nullable=False)
