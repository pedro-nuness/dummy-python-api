"""
Módulo centralizado para métricas Prometheus.
Fornece classes e funções para instrumentação padronizada da aplicação.
"""
from typing import Dict, Optional
import time
from prometheus_client import Counter, Histogram, Gauge, Summary
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

NAMESPACE = "dummy_api"

HTTP_REQUEST_COUNTER = Counter(
    f"{NAMESPACE}_http_requests_total",
    "Total de requisições HTTP recebidas",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION = Histogram(
    f"{NAMESPACE}_http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["method", "endpoint", "status_code"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    f"{NAMESPACE}_http_requests_in_progress",
    "Número de requisições HTTP em andamento",
    ["method", "endpoint"]
)

FINANCE_API_ERROR_COUNTER = Counter(
    f"{NAMESPACE}_finance_api_errors_total",
    "Total de erros na API de finanças",
    ["endpoint", "error_type"]
)

FINANCE_API_REQUESTS = Counter(
    f"{NAMESPACE}_finance_api_requests_total",
    "Total de requisições à API de finanças",
    ["endpoint", "active_name"]
)

FINANCE_API_DURATION = Histogram(
    f"{NAMESPACE}_finance_api_duration_seconds",
    "Duração das requisições à API de finanças em segundos",
    ["endpoint", "active_name"],
    buckets=[0.1, 0.5, 1, 2.5, 5, 10, 30]
)

CACHE_HITS = Counter(
    f"{NAMESPACE}_cache_hits_total",
    "Total de acertos no cache",
    ["cache_name"]
)

CACHE_MISSES = Counter(
    f"{NAMESPACE}_cache_misses_total",
    "Total de falhas no cache",
    ["cache_name"]
)

EXTERNAL_SERVICE_REQUESTS = Counter(
    f"{NAMESPACE}_external_service_requests_total",
    "Total de requisições a serviços externos",
    ["service_name", "endpoint", "method"]
)

EXTERNAL_SERVICE_ERRORS = Counter(
    f"{NAMESPACE}_external_service_errors_total",
    "Total de erros em requisições a serviços externos",
    ["service_name", "endpoint", "error_type"]
)

EXTERNAL_SERVICE_DURATION = Histogram(
    f"{NAMESPACE}_external_service_duration_seconds",
    "Duração das requisições a serviços externos em segundos",
    ["service_name", "endpoint"],
    buckets=[0.1, 0.5, 1, 2.5, 5, 10, 30]
)

CIRCUIT_BREAKER_STATE = Gauge(
    f"{NAMESPACE}_circuit_breaker_state",
    "Estado atual do Circuit Breaker (0=fechado, 1=aberto)",
    ["service_name"]
)

CIRCUIT_BREAKER_FAILURE_COUNT = Gauge(
    f"{NAMESPACE}_circuit_breaker_failure_count",
    "Contador atual de falhas no Circuit Breaker",
    ["service_name"]
)

CIRCUIT_BREAKER_TRIPPED_TOTAL = Counter(
    f"{NAMESPACE}_circuit_breaker_tripped_total",
    "Total de vezes que o Circuit Breaker foi aberto",
    ["service_name"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware que captura métricas Prometheus para todas as requisições HTTP
    """

    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration = time.time() - start_time
            
            HTTP_REQUEST_COUNTER.labels(
                method=method, endpoint=path, status_code=status_code
            ).inc()
            
            HTTP_REQUEST_DURATION.labels(
                method=method, endpoint=path, status_code=status_code
            ).observe(duration)
            
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()


class MetricsTimer:
    """
    Classe utilitária para medir o tempo de execução de uma operação
    e registrar em um histogram do Prometheus.
    
    Exemplo de uso:
    
    with MetricsTimer(FINANCE_API_DURATION, {"endpoint": "/finance/active", "active_name": "BTC-BRL"}):
        # código a ser medido
    """
    
    def __init__(self, histogram: Histogram, labels: Dict[str, str]):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.histogram.labels(**self.labels).observe(duration)
