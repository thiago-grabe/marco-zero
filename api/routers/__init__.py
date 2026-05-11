from .auth import router as auth_router
from .chat import router as chat_router
from .contracts import router as contracts_router
from .motor import router as motor_router
from .operations import router as operations_router
from .scenarios import router as scenarios_router

__all__ = [
    "auth_router",
    "chat_router",
    "contracts_router",
    "motor_router",
    "operations_router",
    "scenarios_router",
]
