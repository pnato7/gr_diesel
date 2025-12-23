#!/usr/bin/env bash
set -euo pipefail

# wsl_setup_weasy.sh
# Automatiza o setup do ambiente WSL (Ubuntu/Debian) para gerar PDFs com WeasyPrint
# Uso: ./wsl_setup_weasy.sh [--no-test] [--project-dir /path/to/project]

NO_TEST=0
PROJECT_DIR="$(pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-test) NO_TEST=1; shift ;;
    --project-dir) PROJECT_DIR="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--no-test] [--project-dir DIR]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "[wsl_setup_weasy] Projeto: $PROJECT_DIR"

if ! command -v apt >/dev/null 2>&1; then
  echo "Erro: apt não encontrado. Este script é para Ubuntu/Debian em WSL." >&2
  exit 1
fi

SUDO='sudo'

echo "[wsl_setup_weasy] Atualizando pacotes..."
$SUDO apt update
$SUDO apt upgrade -y

PKGS=(build-essential python3-venv python3-dev \
  libcairo2 libpangocairo-1.0-0 libpango-1.0-0 libgdk-pixbuf2.0-0 \
  libffi-dev libglib2.0-0 libgirepository1.0-1 libxml2 libxslt1.1 \
  libjpeg-dev libpng-dev fonts-dejavu-core fonts-noto-core fonts-liberation)

echo "[wsl_setup_weasy] Instalando pacotes do sistema: ${PKGS[*]}"
$SUDO apt install -y "${PKGS[@]}"

# Ir para o diretório do projeto
cd "$PROJECT_DIR"

# Criar venv, ativar e instalar requirements
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "[wsl_setup_weasy] Criando virtualenv em $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

echo "[wsl_setup_weasy] Ativando venv..."
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
  echo "[wsl_setup_weasy] Instalando requirements.txt..."
  pip install -r requirements.txt
else
  echo "[wsl_setup_weasy] requirements.txt não encontrado — instalando WeasyPrint apenas"
  pip install WeasyPrint
fi

# Teste de geração de PDF
if [ "$NO_TEST" -eq 0 ]; then
  echo "[wsl_setup_weasy] Executando teste WeasyPrint (gera test-weasy.pdf)..."
  python - << 'PY'
from weasyprint import HTML
HTML(string='<p>Teste WeasyPrint — OK</p>').write_pdf('test-weasy.pdf')
print('GERADO: test-weasy.pdf')
PY
  echo "[wsl_setup_weasy] Teste concluído. Abra o arquivo com explorer.exe . ou copie para Windows." 
else
  echo "[wsl_setup_weasy] Pulando teste (--no-test)."
fi

echo "[wsl_setup_weasy] Concluído com sucesso ✅"

echo "Dica: para abrir o diretório atual no Windows Explorer use: explorer.exe ."

exit 0
