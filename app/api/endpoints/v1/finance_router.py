from fastapi import APIRouter, Depends, Path, Request
import httpx
from app.api.dependencies import get_http_client
from app.services.coin_desk_api_service import ExternalApiService
from app.schemas.coin_desk import BTCDataResponse
from slowapi.util import get_remote_address
from slowapi import Limiter
from app.core.metrics import (
    FINANCE_API_ERROR_COUNTER,
    FINANCE_API_REQUESTS,
    MetricsTimer,
    FINANCE_API_DURATION
)

router = APIRouter(prefix="/finance", tags=["Finance"])
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/active/{active_name}",
    response_model=BTCDataResponse,
    summary="Busca informações de um ativo financeiro em um serviço externo"
)
@limiter.limit("10/minute")
async def get_integrated_active(
    active_name: str = Path(..., title="O nome do ativo a ser buscado", example="BTC-BRL"),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    request: Request = None
):
    """
    Endpoint que orquestra a busca de informações de um ativo financeiro
    """
    FINANCE_API_REQUESTS.labels(endpoint="/finance/active", active_name=active_name).inc()
    
    service = ExternalApiService(client=http_client)
    
    with MetricsTimer(FINANCE_API_DURATION, {"endpoint": "/finance/active", "active_name": active_name}):
        try:
            external_active_data = await service.get_active_by_name(active_name)
            response = BTCDataResponse(**{"BTC-DATA": external_active_data})
            return response
        except Exception as e:
            FINANCE_API_ERROR_COUNTER.labels(
                endpoint="/finance/active", 
                error_type=e.__class__.__name__
            ).inc()
            
            from app.core.logging import logger
            logger.error(f"Erro no endpoint /finance/active: {e}")
            raise
