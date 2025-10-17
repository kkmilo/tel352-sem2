#!/bin/bash
################################################################################
# Script de Instalación de Dependencias
################################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "INSTALACIÓN DE DEPENDENCIAS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROYECTO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROYECTO_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: No se encontró el entorno virtual"
    echo ""
    echo "Ejecuta primero:"
    echo "   ./scripts/setup_entorno.sh"
    exit 1
fi

source "$VENV_DIR/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Error al activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual activado"
echo ""

if [ ! -f "$PROYECTO_DIR/requirements.txt" ]; then
    echo "⚠️  Creando requirements.txt..."
    cat > "$PROYECTO_DIR/requirements.txt" << 'REQEOF'
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
pillow>=10.0.0
joblib>=1.3.0
scikit-learn>=1.3.0
REQEOF
fi

echo "📦 Instalando dependencias..."
echo ""

pip install -r "$PROYECTO_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "❌ Error durante la instalación"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ DEPENDENCIAS INSTALADAS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Próximo paso:"
echo "   ./scripts/ejecutar_sistema.sh"
echo ""
