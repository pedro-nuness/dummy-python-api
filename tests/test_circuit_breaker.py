import pytest
import asyncio
from app.services.circuit_breaker import AsyncRedisCircuitBreaker
from unittest.mock import patch, MagicMock
import time
from prometheus_client import REGISTRY


@pytest.fixture
def mock_redis():
    with patch('app.services.circuit_breaker.Redis') as mock:
        mock_instance = MagicMock()
        mock.from_url.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_circuit_breaker_fail_and_open(mock_redis):
    """Test that circuit breaker opens after max failures"""
    # Configurar o mock para simular o Redis
    mock_redis.get.side_effect = [
        None,  # get_state - inicialmente None = closed
        "0",   # get_failure_count - inicialmente 0
        "1",   # depois do incr (1ª falha)
        "2",   # depois do incr (2ª falha)
        "3",   # depois do incr (3ª falha)
        "open" # estado após 3 falhas
    ]
    mock_redis.incr.side_effect = ["1", "2", "3"]
    
    # Criar o circuit breaker
    cb = AsyncRedisCircuitBreaker(
        redis_url="redis://fake",
        fail_max=3,
        reset_timeout=30,
        state_name="test_service"
    )
    
    # Verificar estado inicial
    assert await cb.can_execute() is True
    
    # Simular 3 falhas consecutivas
    await cb.fail()
    await cb.fail()
    await cb.fail()
    
    # Verificar que o circuit breaker abriu
    assert await cb.can_execute() is False
    
    # Verificar as métricas
    for metric in REGISTRY.collect():
        if metric.name == "dummy_api_circuit_breaker_state":
            for sample in metric.samples:
                if sample.labels.get('service_name') == 'test_service':
                    assert sample.value == 1.0  # 1 = aberto
        
        if metric.name == "dummy_api_circuit_breaker_tripped_total":
            for sample in metric.samples:
                if sample.labels.get('service_name') == 'test_service':
                    assert sample.value == 1.0  # foi aberto uma vez


@pytest.mark.asyncio
async def test_circuit_breaker_success_and_reset(mock_redis):
    """Test that circuit breaker resets after success"""
    # Configurar o mock
    mock_redis.get.return_value = "closed"
    
    # Criar o circuit breaker
    cb = AsyncRedisCircuitBreaker(
        redis_url="redis://fake",
        fail_max=3,
        reset_timeout=30,
        state_name="test_service"
    )
    
    # Registrar um sucesso deve resetar o contador
    await cb.success()
    
    # Verificar as chamadas ao Redis
    mock_redis.delete.assert_called_once()
    mock_redis.set.assert_called_with('cb:test_service:state', 'closed')


@pytest.mark.asyncio
async def test_circuit_breaker_auto_reset(mock_redis):
    """Test that circuit breaker automatically resets after timeout"""
    # Tempo atual simulado
    current_time = int(time.time())
    
    # Configurar o mock para simular o Redis
    mock_redis.get.side_effect = [
        "open",  # get_state - inicialmente open
        str(current_time - 10),  # open_until já expirou (10 segundos atrás)
        "closed"  # get_state após verificar o tempo
    ]
    
    # Criar o circuit breaker
    cb = AsyncRedisCircuitBreaker(
        redis_url="redis://fake",
        fail_max=3,
        reset_timeout=5,  # 5 segundos
        state_name="test_service"
    )
    
    # Verificar que o circuit breaker vai detectar que o tempo expirou
    assert await cb.can_execute() is True
    
    # Verificar que o estado foi atualizado
    mock_redis.set.assert_called()
