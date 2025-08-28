#!/bin/bash

# Script para gerenciar os serviços Docker da aplicação

function print_help {
    echo "Uso: ./manage-services.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  start       - Inicia todos os serviços"
    echo "  stop        - Para todos os serviços"
    echo "  restart     - Reinicia todos os serviços"
    echo "  logs        - Mostra logs da API"
    echo "  status      - Mostra o status de todos os serviços"
    echo "  build       - Reconstrói a imagem da API"
    echo "  prune       - Remove volumes e containers não utilizados"
    echo "  help        - Mostra esta ajuda"
}

case "$1" in
    start)
        echo "Iniciando todos os serviços..."
        docker-compose up -d
        echo "Serviços disponíveis em:"
        echo "  API: http://localhost:8000"
        echo "  Prometheus: http://localhost:9090"
        echo "  Grafana: http://localhost:3000"
        ;;
    stop)
        echo "Parando todos os serviços..."
        docker-compose down
        ;;
    restart)
        echo "Reiniciando todos os serviços..."
        docker-compose down
        docker-compose up -d
        ;;
    logs)
        echo "Mostrando logs da API..."
        docker-compose logs -f api
        ;;
    status)
        echo "Status dos serviços:"
        docker-compose ps
        ;;
    build)
        echo "Reconstruindo a imagem da API..."
        docker-compose build api
        ;;
    prune)
        echo "Removendo volumes e containers não utilizados..."
        docker-compose down
        docker system prune -f
        ;;
    help|*)
        print_help
        ;;
esac
