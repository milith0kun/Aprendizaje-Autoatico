#!/usr/bin/env bash
# skills.sh — Atajos para el flujo de notebooks Jupyter / Colab
# Proyecto: Aprendizaje Automatico
#
# Uso:
#   bash skills.sh <comando> [argumentos]
#
# Ejemplos:
#   bash skills.sh setup
#   bash skills.sh lab
#   bash skills.sh run "Laboratorios/01 EDA/01. EDA_Calidad_del_aire_plantilla.ipynb"
#   bash skills.sh to-html "Laboratorios/01 EDA/01. EDA_Calidad_del_aire_plantilla.ipynb"
#   bash skills.sh to-py   "Laboratorios/01 EDA/01. EDA_Calidad_del_aire_plantilla.ipynb"
#   bash skills.sh clean   "Laboratorios/01 EDA/01. EDA_Calidad_del_aire_plantilla.ipynb"
#   bash skills.sh list

set -euo pipefail

PYTHON="${PYTHON:-python}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Comandos disponibles:
  setup              Crea/activa venv e instala requirements.txt
  install <pkg...>   Instala paquetes adicionales con pip
  freeze             Actualiza requirements.txt con pip freeze
  lab                Lanza Jupyter Lab
  notebook           Lanza Jupyter Notebook clasico
  run <ipynb>        Ejecuta el notebook in-place (jupyter nbconvert --execute)
  papermill <in> <out> [-p k v ...]  Ejecuta un notebook parametrizado
  to-html <ipynb>    Exporta el notebook a HTML
  to-py <ipynb>      Exporta el notebook a script .py
  to-md <ipynb>      Exporta el notebook a Markdown
  clean <ipynb>      Limpia outputs del notebook (nbstripout)
  list               Lista los notebooks del proyecto
  kernels            Lista kernels Jupyter instalados
  register-kernel <nombre>  Registra el venv actual como kernel
  help               Muestra esta ayuda
EOF
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  setup)
    if [ ! -d ".venv" ]; then
      "$PYTHON" -m venv .venv
    fi
    # shellcheck disable=SC1091
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install -r requirements.txt
    ;;

  install)
    "$PYTHON" -m pip install "$@"
    ;;

  freeze)
    "$PYTHON" -m pip freeze > requirements.txt
    echo "requirements.txt actualizado."
    ;;

  lab)
    "$PYTHON" -m jupyter lab "$@"
    ;;

  notebook)
    "$PYTHON" -m jupyter notebook "$@"
    ;;

  run)
    [ $# -ge 1 ] || { echo "Uso: bash skills.sh run <ipynb>"; exit 1; }
    "$PYTHON" -m jupyter nbconvert --to notebook --execute --inplace "$1"
    ;;

  papermill)
    [ $# -ge 2 ] || { echo "Uso: bash skills.sh papermill <input.ipynb> <output.ipynb> [-p k v ...]"; exit 1; }
    "$PYTHON" -m papermill "$@"
    ;;

  to-html)
    [ $# -ge 1 ] || { echo "Uso: bash skills.sh to-html <ipynb>"; exit 1; }
    "$PYTHON" -m jupyter nbconvert --to html "$1"
    ;;

  to-py)
    [ $# -ge 1 ] || { echo "Uso: bash skills.sh to-py <ipynb>"; exit 1; }
    "$PYTHON" -m jupyter nbconvert --to script "$1"
    ;;

  to-md)
    [ $# -ge 1 ] || { echo "Uso: bash skills.sh to-md <ipynb>"; exit 1; }
    "$PYTHON" -m jupyter nbconvert --to markdown "$1"
    ;;

  clean)
    [ $# -ge 1 ] || { echo "Uso: bash skills.sh clean <ipynb>"; exit 1; }
    "$PYTHON" -m nbstripout "$1"
    ;;

  list)
    find "$PROJECT_ROOT" -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*" -not -path "*/.venv/*" | sort
    ;;

  kernels)
    "$PYTHON" -m jupyter kernelspec list
    ;;

  register-kernel)
    name="${1:-aprendizaje-automatico}"
    "$PYTHON" -m ipykernel install --user --name "$name" --display-name "Python ($name)"
    ;;

  help|-h|--help|"")
    usage
    ;;

  *)
    echo "Comando desconocido: $cmd"
    usage
    exit 1
    ;;
esac
