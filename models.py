from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    short_name: str = Field(unique=True, index=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )