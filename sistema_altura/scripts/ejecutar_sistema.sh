#!/bin/bash
################################################################################
# Script de Ejecución del Sistema de Predicción de Estatura
################################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "SISTEMA DE CAPTURA Y PREDICCIÓN DE ESTATURA"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROYECTO_DIR="$(dirname "$SCRIPT_DIR")"

VENV_DIR="$PROYECTO_DIR/venv"
PROGRAMA="$PROYECTO_DIR/app/captura_y_prediccion.py"

# Verificar si existe el entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: No se encontró el entorno virtual"
    echo ""
    echo "Ejecuta primero:"
    echo "   cd $PROYECTO_DIR"
    echo "   ./scripts/setup_entorno.sh"
    exit 1
fi

# Verificar si existe el programa principal
if [ ! -f "$PROGRAMA" ]; then
    echo "❌ Error: No se encontró el programa principal"
    echo "   Buscando en: $PROGRAMA"
    exit 1
fi

# Activar entorno virtual
source "$VENV_DIR/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Error al activar el entorno virtual"
    exit 1
fi

# Verificar modelo
echo "🔍 Verificando archivos necesarios..."
if [ ! -f "$PROYECTO_DIR/modelos/modelo_altura_random_forest_20251015_215630.pkl" ]; then
    echo "❌ Error: No se encontró el modelo entrenado"
    exit 1
fi

echo "✅ Modelo encontrado"
echo ""

# Verificar calibración
if [ -f "$PROYECTO_DIR/modelos/calibracion_20251015_215630.json" ]; then
    echo "✅ Calibración encontrada"
else
    echo "⚠️  Sin calibración"
fi
echo ""

# Crear carpetas de datos si no existen
mkdir -p "$PROYECTO_DIR/data/capturas"
mkdir -p "$PROYECTO_DIR/data/resultados"

echo "🚀 Iniciando sistema..."
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Cambiar al directorio del proyecto para que las rutas funcionen
cd "$PROYECTO_DIR"

# Ejecutar programa
python "$PROGRAMA"

EXIT_CODE=$?

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Sistema finalizado correctamente"
else
    echo "⚠️  Sistema finalizado con código: $EXIT_CODE"
fi

echo "═══════════════════════════════════════════════════════════════"
echo ""

deactivate 2>/dev/null
exit $EXIT_CODE
