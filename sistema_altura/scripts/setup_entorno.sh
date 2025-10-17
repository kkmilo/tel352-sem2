#!/bin/bash
################################################################################
# Script de Configuración del Entorno Virtual
################################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "CONFIGURACIÓN DEL ENTORNO VIRTUAL"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Obtener directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROYECTO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROYECTO_DIR/venv"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python detectado: $PYTHON_VERSION"
echo ""

# Verificar venv
if ! python3 -m venv --help &> /dev/null; then
    echo "❌ El módulo venv no está disponible"
    exit 1
fi
echo "✅ Módulo venv disponible"
echo ""

# Crear entorno virtual
if [ -d "$VENV_DIR" ]; then
    echo "⚠️  Ya existe un entorno virtual"
    read -p "¿Eliminarlo y crear uno nuevo? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf "$VENV_DIR"
    else
        echo "✅ Usando entorno existente"
        exit 0
    fi
fi

echo "🐍 Creando entorno virtual..."
python3 -m venv "$VENV_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Error al crear el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual creado"
echo ""

source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel --quiet

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ ENTORNO VIRTUAL CONFIGURADO"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📁 Ubicación: $VENV_DIR"
echo ""
echo "🚀 Próximo paso:"
echo "   ./scripts/instalar_dependencias.sh"
echo ""
