# Script para gerenciar os serviços Docker da aplicação

function Print-Help {
    Write-Host "Uso: .\manage-services.ps1 [comando]"
    Write-Host ""
    Write-Host "Comandos:"
    Write-Host "  start-all   - Inicia todos os serviços"
    Write-Host "  start-api   - Inicia apenas o serviço da API"
    Write-Host "  start-monitoring - Inicia apenas os serviços Prometheus e Grafana"    Write-Host "  stop        - Para todos os serviços"
    Write-Host "  restart     - Reinicia todos os serviços"    Write-Host "  sync-time   - Reinicia serviços com sincronização de tempo"
    Write-Host "  check-time  - Verifica sincronização de tempo e tenta resolver"
    Write-Host "  fix-time-windows - Usa configuração específica para Windows com timezone explícito"
    Write-Host "  fix-time    - Executa script de correção completa da sincronização de tempo (requer privilégios admin)"
    Write-Host "  adjust-offset - Calcula e atualiza automaticamente o offset de tempo no Prometheus"
    Write-Host "  logs        - Mostra logs da API"
    Write-Host "  status      - Mostra o status de todos os serviços"
    Write-Host "  build       - Reconstrói a imagem da API"
    Write-Host "  rebuild     - Remove as imagens existentes e reconstrói do zero"
    Write-Host "  prune       - Remove volumes e containers não utilizados"
    Write-Host "  help        - Mostra esta ajuda"
}

$command = $args[0]

switch ($command) {
    "start-all" {
        Write-Host "Iniciando todos os serviços..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "Serviços disponíveis em:" -ForegroundColor Green
        Write-Host "  API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000" -ForegroundColor Cyan
    }
    "start" {
        # Compatibilidade com o comando anterior
        Write-Host "Iniciando todos os serviços..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "Serviços disponíveis em:" -ForegroundColor Green
        Write-Host "  API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000" -ForegroundColor Cyan
    }
    "start-api" {
        Write-Host "Iniciando apenas o serviço da API..." -ForegroundColor Green
        docker-compose up -d api
        Write-Host "API disponível em: http://localhost:8000" -ForegroundColor Cyan
    }
    "start-monitoring" {
        Write-Host "Iniciando apenas os serviços de monitoramento..." -ForegroundColor Green
        docker-compose up -d prometheus grafana
        Write-Host "Serviços disponíveis em:" -ForegroundColor Green
        Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000" -ForegroundColor Cyan
    }
    "stop" {
        Write-Host "Parando todos os serviços..." -ForegroundColor Yellow
        docker-compose down
    }
    "restart" {
        Write-Host "Reiniciando todos os serviços..." -ForegroundColor Yellow
        docker-compose down
        docker-compose up -d
    }
    "logs" {
        Write-Host "Mostrando logs da API..." -ForegroundColor Cyan
        docker-compose logs -f api
    }
    "status" {
        Write-Host "Status dos serviços:" -ForegroundColor Cyan
        docker-compose ps
    }
    "build" {
        Write-Host "Reconstruindo a imagem da API..." -ForegroundColor Yellow
        docker-compose build api
    }
    "rebuild" {
        Write-Host "Removendo imagens e reconstruindo do zero..." -ForegroundColor Magenta
        docker-compose down
        docker rmi dummy-python-api_api -f
        docker-compose build --no-cache api
        Write-Host "Reconstrução completa. Use 'start' para iniciar os serviços." -ForegroundColor Green
    }    "prune" {
        Write-Host "Removendo volumes e containers não utilizados..." -ForegroundColor Red
        docker-compose down
        docker system prune -f
    }    "sync-time" {
        Write-Host "Reiniciando serviços com sincronização de tempo..." -ForegroundColor Cyan
        docker-compose down
        Write-Host "Verificando hora do sistema..." -ForegroundColor Yellow
        Get-Date
        Write-Host "Reiniciando contêineres com configurações de sincronização de tempo..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "Serviços reiniciados. Aguarde alguns segundos para a sincronização completa." -ForegroundColor Cyan
    }    "check-time" {
        Write-Host "Verificando sincronização de tempo do Prometheus..." -ForegroundColor Cyan
        .\check-timesync.ps1
    }    "fix-time-windows" {
        Write-Host "Usando configuração específica para Windows com timezone explícito..." -ForegroundColor Cyan
        docker-compose -f docker-compose.windows.yml down
        Write-Host "Removendo contêineres existentes..." -ForegroundColor Yellow
        docker-compose -f docker-compose.windows.yml up -d
        Write-Host "Serviços iniciados com configuração Windows-friendly." -ForegroundColor Green
        Write-Host "Serviços disponíveis em:" -ForegroundColor Green
        Write-Host "  API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000" -ForegroundColor Cyan
    }    "fix-time" {
        Write-Host "Iniciando script de correção completa da sincronização de tempo..." -ForegroundColor Magenta
        Write-Host "AVISO: Este comando requer privilégios de administrador." -ForegroundColor Yellow
        
        # Verifica se está sendo executado como administrador
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-Host "Este comando precisa ser executado como administrador." -ForegroundColor Red
            Write-Host "Por favor, abra o PowerShell como administrador e execute:" -ForegroundColor Yellow
            Write-Host ".\fix-time.ps1" -ForegroundColor White -BackgroundColor DarkBlue
        }
        else {
            # Executa o script de correção de tempo
            & .\fix-time.ps1
        }
    }    "adjust-offset" {
        Write-Host "Calculando e atualizando o offset de tempo no Prometheus..." -ForegroundColor Cyan
        
        # Executa o script para calcular e ajustar o offset de tempo
        & .\adjust-time-offset.ps1 -Apply
        
        $answer = Read-Host "Deseja reiniciar os serviços para aplicar as mudanças? (S/N)"
        if ($answer -eq "S" -or $answer -eq "s") {
            Write-Host "Reiniciando apenas o serviço Prometheus..." -ForegroundColor Yellow
            docker-compose restart prometheus
            
            Write-Host "Serviço Prometheus reiniciado. Aguardando inicialização..." -ForegroundColor Cyan
            Start-Sleep -Seconds 5
            
            Write-Host "Verificando sincronização após ajuste..." -ForegroundColor Cyan
            & .\check-timesync.ps1
        }
        
        Write-Host "Para consultas com ajuste de offset, você pode usar:" -ForegroundColor Cyan
        Write-Host "  .\query-prometheus.ps1 -Query 'sua_consulta'" -ForegroundColor White -BackgroundColor DarkBlue
    }
    default {
        Print-Help
    }
}
