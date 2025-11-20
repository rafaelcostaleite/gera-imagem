from sqlalchemy import (
    Column, Integer, String, DateTime, Float, ForeignKey,
    Text, Boolean, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


# Enums
class CaseStatusEnum(str, enum.Enum):
    ABERTO = "Aberto"
    EM_ATENDIMENTO = "Em atendimento"
    SOLUCIONADO = "Solucionado"
    CONCLUIDO = "Concluído"
    CANCELADO = "Cancelado"


class CaseCategoryEnum(str, enum.Enum):
    CORRETIVA = "Corretiva"
    SUPORTE = "Suporte"
    REQUISICOES = "Requisições"
    PREVENTIVAS = "Preventivas"
    INTERVENCOES = "Intervenções"
    INTERVENCAO_EXTRACAO_DADOS = "Intervenção Extração de dados"
    MELHORIAS_SISTEMAS = "Melhorias em sistemas"


class CaseTypeEnum(str, enum.Enum):
    PROBLEMA = "Estou com um problema"
    DUVIDA = "Tenho uma dúvida"
    REQUISICAO = "Quero pedir algo"
    MELHORIA = "Solicitação de melhorias"


class TaskTypeEnum(str, enum.Enum):
    LEVANTAMENTO = "01-Levantamento/Documentação/Especificação"
    DESENVOLVIMENTO = "02-Parametrização/Desenvolvimento"
    HOMOLOGACAO = "03-Homoloção/Teste/GMUD"
    REVISAO_PAR = "04-Revisão em par"
    REVISAO_SM = "05-Revisão SM"
    PRODUCAO = "06-Entrada em produção"
    NAO_CLASSIFICADO = "0-Não classificado"


# Tabela associativa para casos e sprints (muitos para muitos)
case_sprint_association = Table(
    'case_sprint',
    Base.metadata,
    Column('case_id', Integer, ForeignKey('cases.id')),
    Column('sprint_id', Integer, ForeignKey('sprints.id'))
)


class User(Base):
    """Modelo de Usuário"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    owned_cases = relationship("Case", foreign_keys="Case.owner_id", back_populates="owner")
    assigned_cases = relationship("Case", foreign_keys="Case.technician_id", back_populates="technician")
    time_entries = relationship("TimeEntry", back_populates="user")
    created_cases = relationship("Case", foreign_keys="Case.requester_id", back_populates="requester")


class Team(Base):
    """Modelo de Equipe"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    cases = relationship("Case", back_populates="team")


class Service(Base):
    """Modelo de Serviço (Árvore de Serviços)"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    parent = relationship("Service", remote_side=[id], backref="children")
    cases = relationship("Case", back_populates="service")


class Case(Base):
    """Modelo de Caso (Chamado)"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Tipo e Categoria
    case_type = Column(Enum(CaseTypeEnum), nullable=False)
    category = Column(Enum(CaseCategoryEnum), nullable=True)  # Definido após classificação

    # Status
    status = Column(Enum(CaseStatusEnum), default=CaseStatusEnum.ABERTO, nullable=False)

    # Relacionamentos com usuários
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Quem abriu
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Dono (gestor)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Técnico responsável

    # Equipe e Serviço
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    # Datas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    solved_at = Column(DateTime(timezone=True), nullable=True)  # Data de solução
    closed_at = Column(DateTime(timezone=True), nullable=True)  # Data de conclusão
    cancelled_at = Column(DateTime(timezone=True), nullable=True)  # Data de cancelamento

    # Relacionamentos
    requester = relationship("User", foreign_keys=[requester_id], back_populates="created_cases")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_cases")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="assigned_cases")
    team = relationship("Team", back_populates="cases")
    service = relationship("Service", back_populates="cases")
    time_entries = relationship("TimeEntry", back_populates="case", cascade="all, delete-orphan")
    sprints = relationship("Sprint", secondary=case_sprint_association, back_populates="cases")


class TimeEntry(Base):
    """Modelo de Apontamento de Tempo"""
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Data do apontamento
    entry_date = Column(DateTime(timezone=True), nullable=False)

    # Tempo
    hours_spent = Column(String(5), nullable=False)  # Formato HH:MM
    hours_decimal = Column(Float, nullable=False)  # Formato decimal (ex: 0.5 para 30min)

    # Descrição e tipo
    description = Column(Text, nullable=False)
    task_type = Column(Enum(TaskTypeEnum), default=TaskTypeEnum.NAO_CLASSIFICADO, nullable=False)

    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    case = relationship("Case", back_populates="time_entries")
    user = relationship("User", back_populates="time_entries")


class ClosingPeriod(Base):
    """Modelo de Período de Fechamento de Apontamentos"""
    __tablename__ = "closing_periods"

    id = Column(Integer, primary_key=True, index=True)
    closing_date = Column(DateTime(timezone=True), nullable=False, unique=True)
    description = Column(String(255))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Sprint(Base):
    """Modelo de Sprint para Planejamento"""
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Datas da sprint
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)

    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    cases = relationship("Case", secondary=case_sprint_association, back_populates="sprints")
