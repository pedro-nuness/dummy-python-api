import httpx
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.exceptions import ExternalAPIServiceError
from app.schemas.api import BTCData
from app.services.circuit_breaker import AsyncRedisCircuitBreaker

RETRY_STRATEGY = retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)

breaker = AsyncRedisCircuitBreaker(
    redis_url="redis://localhost:6379/0",
    fail_max=settings.CIRCUIT_BREAKER_FAIL_MAX,
    reset_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT,
    state_name="external_api"
)

class ExternalApiService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.EXTERNAL_API_BASE_URL

    @RETRY_STRATEGY
    async def get_active_by_name(self, active: str) -> BTCData:
        request_url = f"{self.base_url}/index/cc/v1/latest/tick?market=cadli&instruments={active}&apply_mapping=true"
        print("Fetching data from external API..., url:", request_url)
        if not await breaker.can_execute():
            raise ExternalAPIServiceError("Circuit Breaker está aberto. Tente novamente mais tarde.")
        try:
            response = await self.client.get(request_url)
            response.raise_for_status()
            await breaker.success()
            data = response.json()
            btc_data_dict = data["Data"][active]
            print("Data fetched successfully:", btc_data_dict)
            return BTCData(**btc_data_dict)
        except httpx.HTTPStatusError as e:
            await breaker.fail()
            if e.response.status_code == 404:
                raise ExternalAPIServiceError(f"Ativo {active} não encontrado no serviço externo.")
            raise
        except Exception as e:
            await breaker.fail()
            raise ExternalAPIServiceError(f"Erro inesperado na comunicação com a API externa: {e}")