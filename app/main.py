from fastapi import FastAPI
from pybreaker import CircuitBreakerError
from app.core.exceptions import (
    ExternalAPIServiceError, 
    external_api_service_exception_handler, 
    circuit_breaker_open_exception_handler,
    rate_limit_exceeded_handler
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
from app.api.endpoints.v1.finance_router import router as finance_router
from app.core.metrics import PrometheusMiddleware
from prometheus_client import make_asgi_app
from app.core.logging import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicação FastAPI iniciada.")
    yield
    logger.info("Aplicação FastAPI finalizada.")

app = FastAPI(
    title="Serviço de Integração de APIs",
    description="API para integração e consulta de ativos financeiros em serviços externos.\n\nPrincipais recursos:\n- Consulta de dados de ativos financeiros (ex: BTC-BRL)\n- Circuit Breaker para resiliência\n- Retentativas automáticas\n- Tratamento detalhado de erros\n\nAcesse /docs para a documentação interativa gerada automaticamente pelo Swagger UI.",
    version="1.0.0",
    contact={
        "name": "Pedro Nunes",
        "email": "skytlepedro@hotmail.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_exception_handler(429, rate_limit_exceeded_handler)
app.add_exception_handler(ExternalAPIServiceError, external_api_service_exception_handler)
app.add_exception_handler(CircuitBreakerError, circuit_breaker_open_exception_handler)

app.include_router(finance_router, prefix="/api/v1")
app.add_middleware(PrometheusMiddleware)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/", tags=["Health Check"])
def read_root():
    logger.info("Health check solicitado.")
    return {"status": "ok"}