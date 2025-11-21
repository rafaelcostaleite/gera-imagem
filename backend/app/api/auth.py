from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.services.auth_service import ad_auth_service
from app.models.models import User
from app.schemas.auth import Token, Login
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint de login - Autentica usuário via Active Directory
    Em modo de desenvolvimento, aceita senha padrão 123456
    """
    user_info = None

    # Modo de desenvolvimento: aceita senha padrão 123456
    if settings.DEVELOPMENT_MODE:
        logger.info(f"Modo de desenvolvimento ativo - tentando login para {form_data.username}")
        if form_data.password == settings.DEV_DEFAULT_PASSWORD:
            # Autenticação bem-sucedida com senha padrão
            user_info = {
                'username': form_data.username,
                'email': f"{form_data.username}@dev.local",
                'full_name': form_data.username.title()
            }
            logger.info(f"Login em modo dev com senha padrão para {form_data.username}")
        else:
            # Tenta autenticar no AD mesmo em dev (para ter opção)
            user_info = ad_auth_service.authenticate(form_data.username, form_data.password)
    else:
        # Modo produção: apenas AD
        user_info = ad_auth_service.authenticate(form_data.username, form_data.password)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar se o usuário já existe no banco
    user = db.query(User).filter(User.username == user_info['username']).first()

    # Se não existir, criar usuário
    if not user:
        user = User(
            username=user_info['username'],
            email=user_info['email'],
            full_name=user_info['full_name'],
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Novo usuário criado: {user.username}")

    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
async def login_json(
    login_data: Login,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login alternativo que aceita JSON
    Em modo de desenvolvimento, aceita senha padrão 123456
    """
    user_info = None

    # Modo de desenvolvimento: aceita senha padrão 123456
    if settings.DEVELOPMENT_MODE:
        logger.info(f"Modo de desenvolvimento ativo - tentando login para {login_data.username}")
        if login_data.password == settings.DEV_DEFAULT_PASSWORD:
            # Autenticação bem-sucedida com senha padrão
            user_info = {
                'username': login_data.username,
                'email': f"{login_data.username}@dev.local",
                'full_name': login_data.username.title()
            }
            logger.info(f"Login em modo dev com senha padrão para {login_data.username}")
        else:
            # Tenta autenticar no AD mesmo em dev (para ter opção)
            user_info = ad_auth_service.authenticate(login_data.username, login_data.password)
    else:
        # Modo produção: apenas AD
        user_info = ad_auth_service.authenticate(login_data.username, login_data.password)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar se o usuário já existe no banco
    user = db.query(User).filter(User.username == user_info['username']).first()

    # Se não existir, criar usuário
    if not user:
        user = User(
            username=user_info['username'],
            email=user_info['email'],
            full_name=user_info['full_name'],
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Novo usuário criado: {user.username}")

    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
