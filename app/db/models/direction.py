"""
Direction model for data validation.

Pydantic model for direction/specialization data.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Direction(BaseModel):
    """Direction data model."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200, description="Direction name")
    course: int = Field(..., ge=1, le=4, description="Course number (1-4)")
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class DirectionCreate(BaseModel):
    """Model for creating new direction."""
    
    name: str = Field(..., min_length=1, max_length=200)
    course: int = Field(..., ge=1, le=4)
