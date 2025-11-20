from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import Case, User, CaseStatusEnum
from app.schemas.case import (
    Case as CaseSchema,
    CaseCreate,
    CaseUpdate,
    CaseClassify,
    CaseStatusUpdate,
    CaseWithDetails
)

router = APIRouter()


@router.post("/", response_model=CaseSchema, status_code=status.HTTP_201_CREATED)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Criar novo caso"""
    new_case = Case(
        title=case_data.title,
        description=case_data.description,
        case_type=case_data.case_type,
        service_id=case_data.service_id,
        requester_id=current_user.id,
        status=CaseStatusEnum.ABERTO
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case


@router.get("/", response_model=List[CaseWithDetails])
def list_cases(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar casos"""
    query = db.query(Case)

    # Filtrar por status se fornecido
    if status:
        query = query.filter(Case.status == status)

    cases = query.offset(skip).limit(limit).all()

    # Enriquecer com informações adicionais
    result = []
    for case in cases:
        case_dict = {
            **case.__dict__,
            "requester_name": case.requester.full_name if case.requester else None,
            "owner_name": case.owner.full_name if case.owner else None,
            "technician_name": case.technician.full_name if case.technician else None,
            "team_name": case.team.name if case.team else None,
            "service_name": case.service.name if case.service else None,
            "total_hours": sum([te.hours_decimal for te in case.time_entries]) if case.time_entries else 0.0
        }
        result.append(CaseWithDetails(**case_dict))

    return result


@router.get("/{case_id}", response_model=CaseWithDetails)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter detalhes de um caso"""
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    case_dict = {
        **case.__dict__,
        "requester_name": case.requester.full_name if case.requester else None,
        "owner_name": case.owner.full_name if case.owner else None,
        "technician_name": case.technician.full_name if case.technician else None,
        "team_name": case.team.name if case.team else None,
        "service_name": case.service.name if case.service else None,
        "total_hours": sum([te.hours_decimal for te in case.time_entries]) if case.time_entries else 0.0
    }

    return CaseWithDetails(**case_dict)


@router.put("/{case_id}", response_model=CaseSchema)
def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar caso"""
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    # Atualizar campos fornecidos
    update_data = case_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)

    return case


@router.post("/{case_id}/classify", response_model=CaseSchema)
def classify_case(
    case_id: int,
    classify_data: CaseClassify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Classificar caso - primeira etapa do atendimento"""
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    # Verificar se já foi classificado
    if case.category is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caso já foi classificado"
        )

    # Atualizar categoria e alocações
    case.category = classify_data.category
    case.owner_id = classify_data.owner_id
    case.team_id = classify_data.team_id
    case.technician_id = classify_data.technician_id

    db.commit()
    db.refresh(case)

    return case


@router.post("/{case_id}/status", response_model=CaseSchema)
def update_case_status(
    case_id: int,
    status_data: CaseStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar status do caso"""
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    # Validar transições de status
    if status_data.status == CaseStatusEnum.CANCELADO:
        if case.status not in [CaseStatusEnum.ABERTO, CaseStatusEnum.EM_ATENDIMENTO]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas casos em 'Aberto' ou 'Em atendimento' podem ser cancelados"
            )
        case.cancelled_at = datetime.utcnow()

    elif status_data.status == CaseStatusEnum.SOLUCIONADO:
        case.solved_at = datetime.utcnow()

    elif status_data.status == CaseStatusEnum.CONCLUIDO:
        if case.status != CaseStatusEnum.SOLUCIONADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas casos 'Solucionados' podem ser concluídos"
            )
        case.closed_at = datetime.utcnow()

    case.status = status_data.status
    db.commit()
    db.refresh(case)

    return case


@router.get("/my/cases", response_model=List[CaseWithDetails])
def get_my_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter casos do usuário atual (criados, atribuídos ou como dono)"""
    cases = db.query(Case).filter(
        (Case.requester_id == current_user.id) |
        (Case.technician_id == current_user.id) |
        (Case.owner_id == current_user.id)
    ).all()

    result = []
    for case in cases:
        case_dict = {
            **case.__dict__,
            "requester_name": case.requester.full_name if case.requester else None,
            "owner_name": case.owner.full_name if case.owner else None,
            "technician_name": case.technician.full_name if case.technician else None,
            "team_name": case.team.name if case.team else None,
            "service_name": case.service.name if case.service else None,
            "total_hours": sum([te.hours_decimal for te in case.time_entries]) if case.time_entries else 0.0
        }
        result.append(CaseWithDetails(**case_dict))

    return result
