"""
Ponto de entrada principal para Cloud Run
Versão simplificada e robusta
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Criar aplicação FastAPI básica
app = FastAPI(
    title="Sistema de Otimização de Rotas",
    description="API REST para otimização de rotas de atendimento com algoritmo genético",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ Endpoint raiz da API """
    return {
        "message": "API de Otimização de Rotas - Cloud Run",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """ Verifica o status da API """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """ Status detalhado da API """
    return {
        "service": "genetic-route-optimizer-api",
        "status": "operational",
        "environment": "cloud-run",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
