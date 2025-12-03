"""
User model for data validation.

Pydantic model for user data structure.
"""

from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """User data model."""
    
    id: Optional[int] = None
    tg_id: int = Field(..., description="Telegram user ID")
    name: str = Field(..., min_length=1, max_length=100, description="Student name")
    course: int = Field(..., ge=1, le=4, description="Course number (1-4)")
    direction_id: int = Field(..., description="Direction ID")
    remind_before: bool = Field(default=True, description="Enable 5-min reminders")
    paused_until: Optional[str] = None  # ISO date string
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Model for creating new user."""
    
    tg_id: int
    name: str = Field(..., min_length=1, max_length=100)
    course: int = Field(..., ge=1, le=4)
    direction_id: int
    remind_before: bool = True
