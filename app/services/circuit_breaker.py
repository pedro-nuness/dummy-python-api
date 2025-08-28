import pybreaker
from functools import wraps
import asyncio
from app.core.logging import logger
from app.core.metrics import (
    CIRCUIT_BREAKER_STATE,
    CIRCUIT_BREAKER_FAILURE_COUNT,
    CIRCUIT_BREAKER_TRIPPED_TOTAL
)

class StateListener(pybreaker.CircuitBreakerListener):
    def __init__(self, state_name):
        self.state_name = state_name
    
    def state_change(self, cb, old_state, new_state):
        if new_state.name == 'open':
            CIRCUIT_BREAKER_STATE.labels(service_name=self.state_name).set(1)
            CIRCUIT_BREAKER_TRIPPED_TOTAL.labels(service_name=self.state_name).inc()
            logger.warning(f"Circuit Breaker {self.state_name} foi aberto")
        elif new_state.name == 'closed':
            CIRCUIT_BREAKER_STATE.labels(service_name=self.state_name).set(0)
            CIRCUIT_BREAKER_FAILURE_COUNT.labels(service_name=self.state_name).set(0)
            logger.info(f"Circuit Breaker {self.state_name} foi fechado")
        elif new_state.name == 'half-open':
            logger.info(f"Circuit Breaker {self.state_name} está em modo de teste (half-open)")

class FailureListener(pybreaker.CircuitBreakerListener):
    def __init__(self, state_name):
        self.state_name = state_name
    
    def failure(self, cb, exc):
        count = cb.fail_counter
        CIRCUIT_BREAKER_FAILURE_COUNT.labels(service_name=self.state_name).set(count)
        logger.info(f"Circuit Breaker {self.state_name}: {count}/{cb.fail_max} falhas")

class AsyncCircuitBreaker:
    """
    Implementação assíncrona de Circuit Breaker usando a biblioteca pybreaker.
    Esta implementação é thread-safe e não requer Redis ou outra infraestrutura externa.
    
    O Circuit Breaker possui três estados:
    - closed: o circuito está fechado e as requisições são permitidas
    - open: o circuito está aberto e as requisições são rejeitadas
    - half-open: o circuito está em modo de teste após o timeout de reset
    
    Quando o número de falhas consecutivas atinge fail_max, o circuito é aberto.
    O circuito permanece aberto por reset_timeout segundos e depois é fechado novamente.
    """
    def __init__(self, fail_max, reset_timeout, state_name, **kwargs):
        """
        Inicializa o Circuit Breaker.
        
        Args:
            fail_max: Número máximo de falhas consecutivas antes de abrir o circuito
            reset_timeout: Tempo em segundos para resetar o circuito após estar aberto
            state_name: Nome do serviço/estado para identificação nas métricas
        """
        self.state_name = state_name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        
        CIRCUIT_BREAKER_STATE.labels(service_name=self.state_name).set(0)
        CIRCUIT_BREAKER_FAILURE_COUNT.labels(service_name=self.state_name).set(0)
        
        listeners = [
            StateListener(state_name),
            FailureListener(state_name)
        ]
        
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            exclude=[KeyError],
            listeners=listeners,
            name=state_name
        )
        
        logger.info(f"Circuit Breaker inicializado para {state_name} com fail_max={fail_max}, reset_timeout={reset_timeout}s")

    async def can_execute(self):
        """Verifica se o circuito está fechado e permite a execução"""
        return self.breaker.current_state != 'open'
    
    async def success(self):
        """Registra um sucesso no circuito""" 
        pass
    
    async def fail(self):
        """Registra uma falha no circuito"""
        pass

    async def execute(self, func, *args, **kwargs):
        """
        Executa uma função assíncrona protegida pelo circuit breaker

        Args:
            func: Função assíncrona a ser executada
            *args, **kwargs: Argumentos para a função
            
        Returns:
            O resultado da função se bem-sucedida
            
        Raises:
            CircuitBreakerError: Se o circuito estiver aberto
            Exception: Qualquer exceção levantada pela função
        """
        @self.breaker
        async def wrapped_func():
            return await func(*args, **kwargs)
        
        return await wrapped_func()
