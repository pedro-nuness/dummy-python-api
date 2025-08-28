# Visualização de Métricas com Prometheus e Grafana

Este documento descreve como configurar e visualizar as métricas da aplicação, incluindo métricas do Circuit Breaker, usando Prometheus e Grafana.

## Configuração

O projeto inclui um arquivo `docker-compose.yml` que configura:
- Prometheus - para coletar e armazenar métricas
- Grafana - para visualizar métricas em dashboards interativos
- Redis - para armazenar o estado do Circuit Breaker

## Como iniciar os serviços

Execute o seguinte comando na raiz do projeto:

```powershell
docker-compose up -d
```

Isso iniciará:
- API FastAPI na porta 8000
- Prometheus na porta 9090
- Grafana na porta 3000
- Redis na porta 6379

Todos os serviços estão configurados para trabalhar juntos dentro de uma rede Docker.

## Como acessar o Grafana

1. Acesse http://localhost:3000
2. Faça login com:
   - Usuário: `admin`
   - Senha: `admin`
3. Após o primeiro login, será solicitado que você altere a senha (opcional)

## Configuração do Datasource no Grafana

Ao usar o Grafana pela primeira vez, você precisará configurar o Prometheus como fonte de dados:

1. Acesse "Configuration" -> "Data Sources"
2. Clique em "Add data source"
3. Selecione "Prometheus"
4. Configure:
   - URL: `http://prometheus:9090`
   - Access: `Browser` (ou `Server` se tiver problemas)
5. Clique em "Save & Test"

## Importando os Dashboards

### Dashboard de Circuit Breaker

O projeto inclui um dashboard pré-configurado para monitoramento do Circuit Breaker:

1. No Grafana, acesse "Create" -> "Import"
2. Clique em "Upload JSON file" e selecione `grafana/dashboards/circuit_breaker_dashboard.json`
3. Selecione o datasource Prometheus configurado anteriormente
4. Clique em "Import"

### Dashboard de Endpoints HTTP

O projeto também inclui um dashboard para monitorar as chamadas aos endpoints HTTP:

1. No Grafana, acesse "Create" -> "Import"
2. Clique em "Upload JSON file" e selecione `grafana/dashboards/http_endpoints_dashboard.json`
3. Selecione o datasource Prometheus configurado anteriormente
4. Clique em "Import"

## Métricas disponíveis

### Circuit Breaker
- **Estado do Circuit Breaker**: Mostra se o Circuit Breaker está aberto (1) ou fechado (0)
- **Contador de Falhas**: Exibe o número atual de falhas antes de abrir o Circuit Breaker
- **Contador de Disparo**: Mostra quantas vezes o Circuit Breaker foi aberto

### API e Serviços
- **Duração das Requisições**: Mostra o tempo médio, p50 e p95 das requisições à API
- **Total de Requisições**: Exibe o número total de requisições à API
- **Total de Erros**: Mostra o número total de erros ocorridos

### Endpoints HTTP
- **Requisições por Segundo**: Taxa de requisições por segundo para cada endpoint
- **Total de Requisições por Endpoint**: Número total de requisições por endpoint
- **Tempo de Resposta por Endpoint**: Tempo médio de resposta para cada endpoint
- **Requisições em Andamento**: Número atual de requisições em processamento
- **Distribuição por Status Code**: Visualização da distribuição de códigos de status HTTP
- **Sucesso vs Erro**: Taxa de requisições com sucesso vs erro por segundo

## Simulando falhas para visualização

Para testar o funcionamento do Circuit Breaker e visualizar as métricas:

1. Certifique-se de que todos os serviços estão em execução:
   ```powershell
   docker-compose ps
   ```

2. Simule falhas fazendo requisições para um endpoint inválido:
   ```powershell
   curl -X GET "http://localhost:8000/api/v1/finance/active/INVALID-ASSET"
   ```

3. Observe o dashboard no Grafana para ver:
   - O contador de falhas aumentando
   - O Circuit Breaker mudando para estado "aberto" após atingir o limite
   - O contador de disparos incrementando

4. Após o tempo de reset configurado, observe o Circuit Breaker retornando para o estado "fechado"
