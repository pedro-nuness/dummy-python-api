import httpx
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.exceptions import ExternalAPIServiceError
from app.schemas.coin_desk import BTCData
from app.services.circuit_breaker import AsyncCircuitBreaker
from app.core.logging import logger

from app.core.metrics import (
    EXTERNAL_SERVICE_REQUESTS,
    EXTERNAL_SERVICE_ERRORS,
    EXTERNAL_SERVICE_DURATION,
    MetricsTimer
)

RETRY_STRATEGY = retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)

breaker = AsyncCircuitBreaker(
    fail_max=settings.CIRCUIT_BREAKER_FAIL_MAX,
    reset_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT,
    state_name="coin_desk_api"  
)

class ExternalApiService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.EXTERNAL_API_BASE_URL
        
    @RETRY_STRATEGY
    async def get_active_by_name(self, active: str) -> BTCData:
        request_url = f"{self.base_url}/index/cc/v1/latest/tick?market=cadli&instruments={active}&apply_mapping=true"
        endpoint = "/index/cc/v1/latest/tick"
        service_name = "coin_desk_api"
        
        EXTERNAL_SERVICE_REQUESTS.labels(
            service_name=service_name,
            endpoint=endpoint,
            method="GET"
        ).inc()
        
        logger.info(f"Fetching data from external API..., url: {request_url}")
        
        async def fetch_data():
            with MetricsTimer(EXTERNAL_SERVICE_DURATION, {"service_name": service_name, "endpoint": endpoint}):
                response = await self.client.get(request_url)
                response.raise_for_status()
                data = response.json()
                btc_data_dict = data["Data"][active]
                return BTCData(**btc_data_dict)
        
        try:
            return await breaker.execute(fetch_data)
        except pybreaker.CircuitBreakerError:
            EXTERNAL_SERVICE_ERRORS.labels(
                service_name=service_name,
                endpoint=endpoint,
                error_type="CircuitBreakerOpen"
            ).inc()
            raise ExternalAPIServiceError("Circuit Breaker está aberto. Tente novamente mais tarde.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            EXTERNAL_SERVICE_ERRORS.labels(
                service_name=service_name,
                endpoint=endpoint,
                error_type=f"HTTPStatusError_{e.response.status_code}"
            ).inc()
            
            if e.response.status_code == 404:
                raise ExternalAPIServiceError(f"Ativo {active} não encontrado no serviço externo.")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na comunicação com a API externa: {e}")
            
            EXTERNAL_SERVICE_ERRORS.labels(
                service_name=service_name,
                endpoint=endpoint,
                error_type=e.__class__.__name__
            ).inc()
            
            raise ExternalAPIServiceError(f"Erro inesperado na comunicação com a API externa: {e}")
