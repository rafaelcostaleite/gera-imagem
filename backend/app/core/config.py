from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Banco de dados
    DATABASE_URL: str = "postgresql://admin:admin123@db:5432/it_cases"

    # Segurança
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Active Directory / LDAP
    AD_SERVER: str = "ldap://your-ad-server.com"
    AD_DOMAIN: str = "your-domain.com"
    AD_BASE_DN: str = "DC=your-domain,DC=com"
    AD_USE_SSL: bool = False

    # Desenvolvimento
    DEVELOPMENT_MODE: bool = True  # True para usar senha padrão 123456
    DEV_DEFAULT_PASSWORD: str = "123456"

    # Aplicação
    PROJECT_NAME: str = "Sistema de Gestão de Casos TI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
