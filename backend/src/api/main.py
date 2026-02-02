from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging

from core.config import settings, Environment
from infra.database import get_db, async_create_tables
from api.routes import operadoras, analytics, logs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        await async_create_tables()
        logger.info("Database tables verified")
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="API para análise de dados das operadoras de saúde ANS",
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Configurar origens CORS permitidas
allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# Em produção, permitir qualquer subdomínio do Vercel
if settings.environment == Environment.PRODUCTION:
    allowed_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Permite qualquer deploy do Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para prevenir cache em endpoints de API
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)


app.include_router(operadoras.router, prefix="/api/operadoras", tags=["operadoras"])
app.include_router(analytics.router, prefix="/api/estatisticas", tags=["estatisticas"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.version,
        "environment": settings.environment.value,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    from datetime import datetime
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
