from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, cases, time_entries, sprints
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Gestão de Casos TI baseado em ITIL"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Autenticação"]
)

app.include_router(
    cases.router,
    prefix=f"{settings.API_V1_STR}/cases",
    tags=["Casos"]
)

app.include_router(
    time_entries.router,
    prefix=f"{settings.API_V1_STR}/time-entries",
    tags=["Apontamentos"]
)

app.include_router(
    sprints.router,
    prefix=f"{settings.API_V1_STR}/sprints",
    tags=["Sprints"]
)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema de Gestão de Casos TI",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
