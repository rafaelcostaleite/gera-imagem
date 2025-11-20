from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import TimeEntry, User, Case, ClosingPeriod, CaseStatusEnum
from app.schemas.time_entry import (
    TimeEntry as TimeEntrySchema,
    TimeEntryCreate,
    TimeEntryUpdate,
    TimeEntryWithUser
)

router = APIRouter()


def convert_hours_to_decimal(hours_str: str) -> float:
    """Converte string HH:MM para decimal"""
    parts = hours_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours + (minutes / 60.0)


def validate_entry_date(entry_date: datetime, db: Session) -> None:
    """Valida se a data do apontamento é válida"""
    # Não pode ser futura
    if entry_date > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data do apontamento não pode ser futura"
        )

    # Verificar período de fechamento
    last_closing = db.query(ClosingPeriod).order_by(
        ClosingPeriod.closing_date.desc()
    ).first()

    if last_closing and entry_date <= last_closing.closing_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data do apontamento está em período fechado. "
                   f"Último fechamento: {last_closing.closing_date.strftime('%d/%m/%Y')}"
        )


@router.post("/", response_model=TimeEntrySchema, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    entry_data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Criar novo apontamento de tempo"""
    # Validar se o caso existe
    case = db.query(Case).filter(Case.id == entry_data.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    # Validar data do apontamento
    validate_entry_date(entry_data.entry_date, db)

    # Converter horas para decimal
    hours_decimal = convert_hours_to_decimal(entry_data.hours_spent)

    # Criar apontamento
    new_entry = TimeEntry(
        case_id=entry_data.case_id,
        user_id=current_user.id,
        entry_date=entry_data.entry_date,
        hours_spent=entry_data.hours_spent,
        hours_decimal=hours_decimal,
        description=entry_data.description,
        task_type=entry_data.task_type
    )

    db.add(new_entry)

    # Se for o primeiro apontamento, mudar status do caso para "Em atendimento"
    if case.status == CaseStatusEnum.ABERTO:
        case.status = CaseStatusEnum.EM_ATENDIMENTO

    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get("/", response_model=List[TimeEntryWithUser])
def list_time_entries(
    skip: int = 0,
    limit: int = 100,
    case_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar apontamentos"""
    query = db.query(TimeEntry)

    # Filtrar por caso se fornecido
    if case_id:
        query = query.filter(TimeEntry.case_id == case_id)

    entries = query.order_by(TimeEntry.entry_date.desc()).offset(skip).limit(limit).all()

    # Enriquecer com informações adicionais
    result = []
    for entry in entries:
        entry_dict = {
            **entry.__dict__,
            "user_name": entry.user.full_name if entry.user else None,
            "case_title": entry.case.title if entry.case else None
        }
        result.append(TimeEntryWithUser(**entry_dict))

    return result


@router.get("/my", response_model=List[TimeEntryWithUser])
def list_my_time_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar apontamentos do usuário atual"""
    entries = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id
    ).order_by(TimeEntry.entry_date.desc()).offset(skip).limit(limit).all()

    result = []
    for entry in entries:
        entry_dict = {
            **entry.__dict__,
            "user_name": entry.user.full_name if entry.user else None,
            "case_title": entry.case.title if entry.case else None
        }
        result.append(TimeEntryWithUser(**entry_dict))

    return result


@router.get("/{entry_id}", response_model=TimeEntryWithUser)
def get_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter detalhes de um apontamento"""
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apontamento não encontrado"
        )

    entry_dict = {
        **entry.__dict__,
        "user_name": entry.user.full_name if entry.user else None,
        "case_title": entry.case.title if entry.case else None
    }

    return TimeEntryWithUser(**entry_dict)


@router.put("/{entry_id}", response_model=TimeEntrySchema)
def update_time_entry(
    entry_id: int,
    entry_data: TimeEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar apontamento"""
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apontamento não encontrado"
        )

    # Apenas o próprio usuário pode editar seus apontamentos
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este apontamento"
        )

    # Validar data se foi alterada
    if entry_data.entry_date:
        validate_entry_date(entry_data.entry_date, db)

    # Atualizar campos fornecidos
    update_data = entry_data.model_dump(exclude_unset=True)

    # Recalcular horas decimais se horas foram atualizadas
    if "hours_spent" in update_data:
        update_data["hours_decimal"] = convert_hours_to_decimal(update_data["hours_spent"])

    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)

    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar apontamento"""
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apontamento não encontrado"
        )

    # Apenas o próprio usuário pode deletar seus apontamentos
    if entry.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar este apontamento"
        )

    # Validar data do apontamento (não pode estar em período fechado)
    validate_entry_date(entry.entry_date, db)

    db.delete(entry)
    db.commit()

    return None
