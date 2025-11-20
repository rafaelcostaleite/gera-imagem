from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.models import CaseStatusEnum, CaseCategoryEnum, CaseTypeEnum


class CaseBase(BaseModel):
    title: str
    description: str
    case_type: CaseTypeEnum
    service_id: Optional[int] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CaseCategoryEnum] = None
    status: Optional[CaseStatusEnum] = None
    owner_id: Optional[int] = None
    technician_id: Optional[int] = None
    team_id: Optional[int] = None
    service_id: Optional[int] = None


class CaseClassify(BaseModel):
    """Schema para classificação do caso"""
    category: CaseCategoryEnum
    owner_id: int
    team_id: int
    technician_id: Optional[int] = None


class CaseStatusUpdate(BaseModel):
    """Schema para atualização de status"""
    status: CaseStatusEnum
    comment: Optional[str] = None


class Case(CaseBase):
    id: int
    category: Optional[CaseCategoryEnum] = None
    status: CaseStatusEnum
    requester_id: int
    owner_id: Optional[int] = None
    technician_id: Optional[int] = None
    team_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    solved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseWithDetails(Case):
    """Case com informações completas"""
    requester_name: Optional[str] = None
    owner_name: Optional[str] = None
    technician_name: Optional[str] = None
    team_name: Optional[str] = None
    service_name: Optional[str] = None
    total_hours: Optional[float] = 0.0
