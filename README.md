# API de Integração com Circuit Breaker

Este projeto implementa uma API de integração usando FastAPI, com uma arquitetura robusta que inclui o padrão Circuit Breaker para maior resiliência.

## Características

- **FastAPI**: Framework moderno para criação de APIs com Python
- **Circuit Breaker**: Implementação do padrão usando `pybreaker` sem dependência de Redis
- **Monitoramento**: Métricas Prometheus e dashboards Grafana
- **Resiliência**: Retentativas automáticas e tratamento de erros
- **Docker**: Configuração completa para ambiente de desenvolvimento e produção

## Arquitetura

A aplicação é composta por:

- **API**: Serviço principal que gerencia as requisições
- **Prometheus**: Coleta e armazena métricas
- **Grafana**: Visualização de métricas em dashboards interativos

O Circuit Breaker foi implementado usando a biblioteca `pybreaker`, eliminando a necessidade de infraestrutura adicional como Redis. Isto simplifica a arquitetura e facilita a escalabilidade.

## Instalação e Execução

### Requisitos

- Docker e Docker Compose
- PowerShell (Windows) ou Bash (Linux/macOS)

### Início Rápido

Para iniciar todos os serviços:

```powershell
# Windows
./manage-services.ps1 start-all

# Linux/macOS
./manage-services.sh start-all
```

Para iniciar apenas a API:

```powershell
# Windows
./manage-services.ps1 start-api

# Linux/macOS
./manage-services.sh start-api
```

### Acessando a API

A API estará disponível em:
- Interface da API: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Métricas Prometheus: http://localhost:8000/metrics

### Monitoramento

O Grafana estará disponível em http://localhost:3000:
- Login padrão: `admin` / `admin`
- Dashboards disponíveis:
  - **Circuit Breaker**: Monitoramento do estado e estatísticas do Circuit Breaker
  - **HTTP Endpoints**: Visualização de chamadas e performance dos endpoints

Para mais detalhes, consulte [Visualização de Métricas](METRICS_VISUALIZATION.md).

### Resolução de Problemas de Sincronização de Tempo (Windows)

Em ambientes Windows, o Docker pode ter problemas de sincronização de tempo entre o host e os contêineres, especialmente com o Prometheus. Isso pode causar erros como "Server time is out of sync" e impedir a visualização correta das métricas.

Para resolver esse problema:

1. **Verificar a sincronização de tempo**:
   ```powershell
   .\manage-services.ps1 check-time
   ```

2. **Usar configuração específica para Windows**:
   ```powershell
   .\manage-services.ps1 fix-time-windows
   ```

3. **Correção completa de sincronização de tempo** (requer privilégios de administrador):
   ```powershell
   # Executar PowerShell como administrador
   .\manage-services.ps1 fix-time
   ```

4. **Diagnóstico manual** (se os passos anteriores não resolverem):
   - Verifique o horário do sistema Windows está sincronizado com um servidor NTP
   - Reinicie o Docker Desktop
   - Consulte a diferença de tempo entre o host e o Prometheus em `http://localhost:9090/api/v1/query?query=time()`

Para informações detalhadas sobre a resolução de problemas de sincronização, consulte [Resolução de Problemas de Sincronização no Windows](TIME_SYNC_WINDOWS.md).

## Uso da API

A API fornece endpoints para consultar ativos financeiros:

```bash
# Obter dados de um ativo específico
curl -X GET "http://localhost:8000/api/v1/finance/active/BTC-BRL"
```

## Configuração

As configurações da aplicação podem ser ajustadas através de variáveis de ambiente ou arquivo `.env`:

- `COIN_DESK_API_LINK`: URL da CoinDesk
- `LOG_LEVEL`: Nível de log (INFO, DEBUG, etc.)
- `CIRCUIT_BREAKER_FAIL_MAX`: Número máximo de falhas antes de abrir o Circuit Breaker
- `CIRCUIT_BREAKER_RESET_TIMEOUT`: Tempo (em segundos) antes de tentar fechar o Circuit Breaker

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit de suas mudanças (`git commit -am 'Adicionar nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um novo Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT.