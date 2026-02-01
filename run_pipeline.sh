#!/bin/bash
#
# Script para instalação de dependências e execução do Data Pipeline
# Healthcare SaaS - Análise de Operadoras ANS
#

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório raiz do projeto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Healthcare SaaS - Data Pipeline${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Função para exibir mensagens
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python 3 está instalado
check_python() {
    log_info "Verificando instalação do Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1)
        log_info "Python encontrado: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1)
        log_info "Python encontrado: $PYTHON_VERSION"
    else
        log_error "Python não encontrado. Por favor, instale o Python 3.10+"
        exit 1
    fi
}

# Criar e ativar ambiente virtual
setup_venv() {
    log_info "Configurando ambiente virtual..."
    
    VENV_PATH="$PROJECT_ROOT/venv"
    
    if [ ! -d "$VENV_PATH" ]; then
        log_info "Criando ambiente virtual em $VENV_PATH..."
        $PYTHON_CMD -m venv "$VENV_PATH"
    else
        log_info "Ambiente virtual já existe."
    fi
    
    # Ativar venv
    source "$VENV_PATH/bin/activate"
    log_info "Ambiente virtual ativado."
}

# Instalar dependências
install_dependencies() {
    log_info "Instalando dependências do projeto..."
    
    pip install --upgrade pip -q
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt" -q
        log_info "Dependências instaladas com sucesso!"
    else
        log_error "Arquivo requirements.txt não encontrado!"
        exit 1
    fi
}

# Executar o pipeline de dados
run_pipeline() {
    cd "$PROJECT_ROOT/data_pipeline"
    
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Etapa 1: Download dos Dados${NC}"
    echo -e "${BLUE}============================================${NC}"
    log_info "Baixando dados da ANS (últimos 3 trimestres)..."
    python download.py
    
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Etapa 2: Enriquecimento dos Dados${NC}"
    echo -e "${BLUE}============================================${NC}"
    log_info "Enriquecendo dados com informações das operadoras..."
    python enrich.py
    
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Etapa 3: Análise e Métricas${NC}"
    echo -e "${BLUE}============================================${NC}"
    log_info "Gerando métricas e relatórios..."
    python analyze.py
    
    cd "$PROJECT_ROOT"
}

# Menu de opções
show_menu() {
    echo ""
    echo "Uso: $0 [opção]"
    echo ""
    echo "Opções:"
    echo "  install     Apenas instalar dependências"
    echo "  pipeline    Apenas executar o pipeline (requer dependências instaladas)"
    echo "  all         Instalar dependências e executar pipeline (padrão)"
    echo "  help        Exibir esta mensagem"
    echo ""
}

# Main
main() {
    local action="${1:-all}"
    
    case "$action" in
        install)
            check_python
            setup_venv
            install_dependencies
            echo ""
            log_info "Instalação concluída! Para executar o pipeline:"
            echo "  source venv/bin/activate"
            echo "  ./run_pipeline.sh pipeline"
            ;;
        pipeline)
            check_python
            setup_venv
            run_pipeline
            echo ""
            echo -e "${GREEN}============================================${NC}"
            echo -e "${GREEN}   Pipeline executado com sucesso!${NC}"
            echo -e "${GREEN}============================================${NC}"
            echo ""
            log_info "Dados processados em: data_pipeline/data/"
            ;;
        all)
            check_python
            setup_venv
            install_dependencies
            run_pipeline
            echo ""
            echo -e "${GREEN}============================================${NC}"
            echo -e "${GREEN}   Pipeline executado com sucesso!${NC}"
            echo -e "${GREEN}============================================${NC}"
            echo ""
            log_info "Dados processados em: data_pipeline/data/"
            ;;
        help|--help|-h)
            show_menu
            ;;
        *)
            log_error "Opção inválida: $action"
            show_menu
            exit 1
            ;;
    esac
}

main "$@"
