"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ItemBase(BaseModel):
    """Base item schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    in_stock: bool = True
    category: Optional[str] = Field(None, max_length=100)


class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item (partial updates allowed)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    in_stock: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)


class ItemResponse(ItemBase):
    """Schema for item response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    framework: str
    version: str
    timestamp: datetime