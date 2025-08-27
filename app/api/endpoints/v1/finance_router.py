from fastapi import APIRouter, Depends, Path, Request
import httpx
from app.api.dependencies import get_http_client
from app.services.coin_desk_api_service import ExternalApiService
from app.schemas.api import BTCDataResponse
from slowapi.util import get_remote_address
from slowapi import Limiter

router = APIRouter(prefix="/finance", tags=["Finance"])
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/active/{active_name}",
    response_model=BTCDataResponse,
    summary="Busca informações de um ativo financeiro em um serviço externo"
)
@limiter.limit("1/minute")
async def get_integrated_active(
    active_name: str = Path(..., title="O nome do ativo a ser buscado", example="BTC-BRL"),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    request: Request = None
):
    """
    Endpoint que orquestra a busca de informações de um ativo financeiro
    """
    service = ExternalApiService(client=http_client)
    external_active_data = await service.get_active_by_name(active_name)
    response = BTCDataResponse(**{"BTC-DATA": external_active_data})
    return response
