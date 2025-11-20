from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import Sprint, User, Case
from app.schemas.sprint import (
    Sprint as SprintSchema,
    SprintCreate,
    SprintUpdate,
    SprintWithCases,
    SprintAddCases
)

router = APIRouter()


@router.post("/", response_model=SprintSchema, status_code=status.HTTP_201_CREATED)
def create_sprint(
    sprint_data: SprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Criar nova sprint"""
    # Validar datas
    if sprint_data.end_date <= sprint_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de término deve ser posterior à data de início"
        )

    new_sprint = Sprint(
        name=sprint_data.name,
        description=sprint_data.description,
        start_date=sprint_data.start_date,
        end_date=sprint_data.end_date,
        is_active=True,
        is_completed=False
    )

    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)

    return new_sprint


@router.get("/", response_model=List[SprintWithCases])
def list_sprints(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar sprints"""
    query = db.query(Sprint)

    if active_only:
        query = query.filter(Sprint.is_active == True, Sprint.is_completed == False)

    sprints = query.order_by(Sprint.start_date.desc()).offset(skip).limit(limit).all()

    # Enriquecer com informações de casos
    result = []
    for sprint in sprints:
        sprint_dict = {
            **sprint.__dict__,
            "case_ids": [case.id for case in sprint.cases],
            "total_cases": len(sprint.cases)
        }
        result.append(SprintWithCases(**sprint_dict))

    return result


@router.get("/{sprint_id}", response_model=SprintWithCases)
def get_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter detalhes de uma sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    sprint_dict = {
        **sprint.__dict__,
        "case_ids": [case.id for case in sprint.cases],
        "total_cases": len(sprint.cases)
    }

    return SprintWithCases(**sprint_dict)


@router.put("/{sprint_id}", response_model=SprintSchema)
def update_sprint(
    sprint_id: int,
    sprint_data: SprintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    # Atualizar campos fornecidos
    update_data = sprint_data.model_dump(exclude_unset=True)

    # Validar datas se ambas estiverem sendo atualizadas
    if "start_date" in update_data and "end_date" in update_data:
        if update_data["end_date"] <= update_data["start_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de término deve ser posterior à data de início"
            )

    for field, value in update_data.items():
        setattr(sprint, field, value)

    db.commit()
    db.refresh(sprint)

    return sprint


@router.post("/{sprint_id}/cases", response_model=SprintWithCases)
def add_cases_to_sprint(
    sprint_id: int,
    cases_data: SprintAddCases,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adicionar casos à sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    # Buscar casos
    cases = db.query(Case).filter(Case.id.in_(cases_data.case_ids)).all()

    if len(cases) != len(cases_data.case_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais casos não foram encontrados"
        )

    # Adicionar casos à sprint
    for case in cases:
        if case not in sprint.cases:
            sprint.cases.append(case)

    db.commit()
    db.refresh(sprint)

    sprint_dict = {
        **sprint.__dict__,
        "case_ids": [case.id for case in sprint.cases],
        "total_cases": len(sprint.cases)
    }

    return SprintWithCases(**sprint_dict)


@router.delete("/{sprint_id}/cases/{case_id}", response_model=SprintWithCases)
def remove_case_from_sprint(
    sprint_id: int,
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remover caso da sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso não encontrado"
        )

    if case in sprint.cases:
        sprint.cases.remove(case)
        db.commit()
        db.refresh(sprint)

    sprint_dict = {
        **sprint.__dict__,
        "case_ids": [case.id for case in sprint.cases],
        "total_cases": len(sprint.cases)
    }

    return SprintWithCases(**sprint_dict)


@router.post("/{sprint_id}/complete", response_model=SprintSchema)
def complete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar sprint como concluída"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    sprint.is_completed = True
    sprint.is_active = False

    db.commit()
    db.refresh(sprint)

    return sprint


@router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint não encontrada"
        )

    # Apenas superusuários podem deletar sprints
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar sprints"
        )

    db.delete(sprint)
    db.commit()

    return None
