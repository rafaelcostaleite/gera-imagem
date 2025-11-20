from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.models.models import TaskTypeEnum


class TimeEntryBase(BaseModel):
    case_id: int
    entry_date: datetime
    hours_spent: str  # Formato HH:MM
    description: str
    task_type: TaskTypeEnum

    @field_validator('hours_spent')
    @classmethod
    def validate_hours_format(cls, v):
        """Valida formato HH:MM"""
        if not v:
            raise ValueError('Horas não podem ser vazias')

        parts = v.split(':')
        if len(parts) != 2:
            raise ValueError('Formato de horas inválido. Use HH:MM')

        try:
            hours = int(parts[0])
            minutes = int(parts[1])

            if hours < 0 or hours > 23:
                raise ValueError('Horas devem estar entre 00 e 23')

            if minutes < 0 or minutes > 59:
                raise ValueError('Minutos devem estar entre 00 e 59')

        except ValueError as e:
            raise ValueError(f'Formato de horas inválido: {str(e)}')

        return v


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    entry_date: Optional[datetime] = None
    hours_spent: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskTypeEnum] = None

    @field_validator('hours_spent')
    @classmethod
    def validate_hours_format(cls, v):
        """Valida formato HH:MM"""
        if v is None:
            return v

        parts = v.split(':')
        if len(parts) != 2:
            raise ValueError('Formato de horas inválido. Use HH:MM')

        try:
            hours = int(parts[0])
            minutes = int(parts[1])

            if hours < 0 or hours > 23:
                raise ValueError('Horas devem estar entre 00 e 23')

            if minutes < 0 or minutes > 59:
                raise ValueError('Minutos devem estar entre 00 e 59')

        except ValueError as e:
            raise ValueError(f'Formato de horas inválido: {str(e)}')

        return v


class TimeEntry(TimeEntryBase):
    id: int
    user_id: int
    hours_decimal: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimeEntryWithUser(TimeEntry):
    """TimeEntry com informações do usuário"""
    user_name: Optional[str] = None
    case_title: Optional[str] = None
