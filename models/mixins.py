from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False)
    updated_on: Optional[datetime] = Field(default=None, nullable=True)
