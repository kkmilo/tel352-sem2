#!/bin/bash
################################################################################
# INICIO RÁPIDO - Sistema de Predicción de Estatura
################################################################################

clear

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROYECTO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROYECTO_DIR"

echo "════════════════════════════════════════════════════════════════════"
echo "  SISTEMA DE CAPTURA Y PREDICCIÓN DE ESTATURA - INICIO RÁPIDO"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Directorio del proyecto: $PROYECTO_DIR"
echo ""
read -p "Presiona ENTER para continuar..."
clear

# Paso 1: Configurar entorno
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "PASO 1/2: CONFIGURACIÓN DEL ENTORNO VIRTUAL"
echo "════════════════════════════════════════════════════════════════════"
echo ""
if [ -f "$PROYECTO_DIR/scripts/setup_entorno.sh" ]; then
    cd "$PROYECTO_DIR"
    ./scripts/setup_entorno.sh
    if [ $? -ne 0 ]; then
        echo "❌ Error en la configuración"
        exit 1
    fi
else
    echo "❌ setup_entorno.sh no encontrado"
    exit 1
fi

read -p "Presiona ENTER para continuar..."
clear

# Paso 2: Instalar dependencias
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "PASO 2/2: INSTALACIÓN DE DEPENDENCIAS"
echo "════════════════════════════════════════════════════════════════════"
echo ""
if [ -f "$PROYECTO_DIR/scripts/instalar_dependencias.sh" ]; then
    cd "$PROYECTO_DIR"
    ./scripts/instalar_dependencias.sh
    if [ $? -ne 0 ]; then
        echo "❌ Error en la instalación"
        exit 1
    fi
else
    echo "❌ instalar_dependencias.sh no encontrado"
    exit 1
fi

clear

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Para ejecutar el sistema:"
echo "   ./scripts/ejecutar_sistema.sh"
echo ""
read -p "¿Ejecutar el sistema ahora? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    clear
    ./scripts/ejecutar_sistema.sh
else
    echo ""
    echo "✅ Listo. Ejecuta './scripts/ejecutar_sistema.sh' cuando quieras."
    echo ""
fi
