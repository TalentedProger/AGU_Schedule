"""
Pair (class) model for data validation.

Pydantic model for schedule pair data.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Pair(BaseModel):
    """Pair (class) data model."""
    
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Class title")
    teacher: str = Field(..., min_length=1, max_length=200, description="Teacher full name")
    room: str = Field(..., min_length=1, max_length=50, description="Room number")
    type: str = Field(default="Лекция", description="Class type")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    time_slot_id: int = Field(..., description="Time slot ID")
    extra_link: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PairCreate(BaseModel):
    """Model for creating new pair."""
    
    title: str = Field(..., min_length=1, max_length=200)
    teacher: str = Field(..., min_length=1, max_length=200)
    room: str = Field(..., min_length=1, max_length=50)
    type: str = "Лекция"
    day_of_week: int = Field(..., ge=0, le=6)
    time_slot_id: int
    extra_link: Optional[str] = None
