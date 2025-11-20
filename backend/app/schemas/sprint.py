from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SprintBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class Sprint(SprintBase):
    id: int
    is_active: bool
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SprintWithCases(Sprint):
    """Sprint com casos associados"""
    case_ids: List[int] = []
    total_cases: int = 0


class SprintAddCases(BaseModel):
    """Schema para adicionar casos a sprint"""
    case_ids: List[int]
