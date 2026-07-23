#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d "$ENV_DIR" ]; then
  echo "Creando ambiente virtual en $ENV_DIR..."
  "$PYTHON_BIN" -m venv "$ENV_DIR"
  echo "Actualizando pip..."
  "$ENV_DIR/bin/python" -m pip install --upgrade pip

  echo "Instalando dependencias desde requirements.txt..."
  "$ENV_DIR/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"
else
  echo "El ambiente virtual $ENV_DIR ya existe."
fi


echo
echo "Ambiente listo."
echo "Para activarlo ejecuta:"
echo "  source Resultados/.venv/bin/activate"
