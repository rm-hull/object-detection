from datetime import datetime
import uuid
from typing import Optional

from sqlmodel import Field, SQLModel

from .mixins import TimestampMixin


class File(TimestampMixin, SQLModel, table=True):

    __tablename__ = "file"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    filename: str = Field(nullable=False)
    scanned: Optional[datetime] = Field(nullable=True)
