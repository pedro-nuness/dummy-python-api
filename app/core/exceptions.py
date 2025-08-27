from fastapi import Request, status
from fastapi.responses import JSONResponse
from pybreaker import CircuitBreakerError
from slowapi.errors import RateLimitExceeded

class ExternalAPIServiceError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

def external_api_service_exception_handler(request: Request, exc: ExternalAPIServiceError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Erro na integração com o serviço externo", "detail": exc.detail},
    )

def circuit_breaker_open_exception_handler(request: Request, exc: CircuitBreakerError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "message": "Serviço externo temporariamente indisponível. Tente novamente mais tarde.",
            "detail": "Circuit Breaker está no estado 'OPEN'.",
        },
    )

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "message": "Limite de requisições excedido",
            "detail": "Você atingiu o limite de requisições permitido. Tente novamente mais tarde."
        },
    )