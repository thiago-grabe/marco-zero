"""
Marco Zero — FastAPI backend
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import auth_router, chat_router, contracts_router, motor_router, operations_router, scenarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Marco Zero API",
    description="Copiloto de quitação imobiliária — motor de cálculo e agentes IA",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(contracts_router)
app.include_router(scenarios_router)
app.include_router(operations_router)
app.include_router(motor_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
