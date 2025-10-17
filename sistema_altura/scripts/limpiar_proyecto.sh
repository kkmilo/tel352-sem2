#!/bin/bash
################################################################################
# Script de Limpieza del Sistema de Predicción de Estatura
################################################################################
# 
# Este script elimina todos los archivos innecesarios y deja solo
# lo esencial para ejecutar el sistema de captura y predicción.
#
################################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "LIMPIEZA DEL SISTEMA DE PREDICCIÓN DE ESTATURA"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  Este script eliminará:"
echo "   • Modelos antiguos"
echo "   • Scripts de entrenamiento"
echo "   • Datasets descargados"
echo "   • Backups y archivos temporales"
echo "   • Cache de Python"
echo "   • Documentación redundante"
echo ""
echo "✅ Se mantendrán:"
echo "   • Modelo más reciente (20251015_215630)"
echo "   • Programa principal (captura_y_prediccion.py)"
echo "   • Dependencias necesarias"
echo "   • README y requirements.txt"
echo ""
read -p "¿Continuar con la limpieza? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Limpieza cancelada"
    exit 1
fi

echo ""
echo "🧹 Iniciando limpieza..."
echo ""

# Contador de archivos eliminados
count=0

# 1. Eliminar modelos antiguos
echo "📦 Eliminando modelos antiguos..."
rm -f modelo_altura_random_forest_20251015_195700.pkl
rm -f modelo_altura_random_forest_20251015_210428.pkl
rm -f scaler_20251015_195700.pkl
rm -f scaler_20251015_210428.pkl
rm -f modelo_metadata_20251015_195700.json
rm -f modelo_metadata_20251015_210428.json
rm -f calibracion_20251015_210428.json
rm -f reporte_calidad_20251015_195659.json
rm -f reporte_calidad_20251015_210427.json
((count += 9))

# 2. Eliminar scripts de entrenamiento y preparación
echo "🗑️  Eliminando scripts de entrenamiento..."
rm -f train_height_model.py
rm -f entrenar_con_datos_reales.py
rm -f generar_dataset_realista.py
rm -f descargar_datasets.py
rm -f descargar_dataset.py
rm -f test_height_estimation.py
rm -f Body_Detection_simple.py
rm -f predict_height.py
rm -f demo_automatizado.py
((count += 9))

# 3. Eliminar scripts de calibración (ya está calibrado)
echo "🔧 Eliminando scripts de calibración..."
rm -f calibrar_modelo.py
rm -f calibrar.sh
rm -f verificar_calibracion.py
rm -f calcular_distancia_optima.py
((count += 4))

# 4. Eliminar documentación redundante
echo "📄 Eliminando documentación redundante..."
rm -f GUIA_CALIBRACION.md
rm -f GUIA_CAPTURA.md
rm -f GUIA_DATOS_REALES.md
rm -f GUIA_DISTANCIA_OPTIMA.md
rm -f GUIA_RAPIDA.md
rm -f LEEME_PRIMERO.md
rm -f LIMPIEZA_COMPLETADA.md
rm -f SISTEMA_CAPTURA_COMPLETADO.md
rm -f SOLUCION_PRECISION.md
rm -f RESUMEN_CALIBRACION.md
rm -f RESUMEN_DISTANCIA.txt
rm -f REPORTE_ENTRENAMIENTO.md
rm -f DATASETS_RECOMENDADOS.md
rm -f QUE_NECESITO_PARA_EJECUTAR.md
rm -f ARCHIVOS_A_MANTENER.txt
((count += 15))

# 5. Eliminar scripts bash antiguos
echo "🔨 Eliminando scripts bash antiguos..."
rm -f iniciar_captura.sh
rm -f ejecutar_demo.sh
rm -f menu_sistema.sh
rm -f test_sistema.sh
((count += 4))

# 6. Eliminar datasets completos
echo "💾 Eliminando datasets..."
rm -rf datasets_reales/
((count += 1))

# 7. Eliminar carpeta de backups
echo "📦 Eliminando backups..."
rm -rf archivos_backup/
((count += 1))

# 8. Eliminar cache de Python
echo "🗂️  Eliminando cache de Python..."
rm -rf __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -exec rm -f {} + 2>/dev/null
find . -type f -name "*.pyo" -exec rm -f {} + 2>/dev/null
((count += 3))

# 9. Limpiar resultados antiguos (opcional - mantener los 3 más recientes)
echo "📊 Limpiando resultados antiguos..."
cd resultados_predicciones/ 2>/dev/null
if [ $? -eq 0 ]; then
    # Mantener solo los 3 más recientes
    ls -t prediccion_*.json | tail -n +4 | xargs rm -f 2>/dev/null
    cd ..
fi

# 10. Limpiar capturas antiguas (opcional - mantener las 5 más recientes)
echo "📸 Limpiando capturas antiguas..."
cd capturas_estatura/ 2>/dev/null
if [ $? -eq 0 ]; then
    # Mantener solo las 5 más recientes
    ls -t *.jpg 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
    ls -t *.png 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
    cd ..
fi

# 11. Eliminar entorno virtual viejo si existe
echo "🐍 Eliminando entorno virtual antiguo..."
if [ -d "venv_height" ]; then
    rm -rf venv_height/
    ((count += 1))
    echo "   ✅ Entorno virtual antiguo eliminado"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ LIMPIEZA COMPLETADA"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Resumen:"
echo "   • Archivos/carpetas eliminados: ~$count"
echo ""
echo "📁 Estructura final:"
echo "   ├── captura_y_prediccion.py          (Programa principal)"
echo "   ├── haarcascade_frontalface_default.xml"
echo "   ├── modelo_altura_random_forest_20251015_215630.pkl"
echo "   ├── scaler_20251015_215630.pkl"
echo "   ├── modelo_metadata_20251015_215630.json"
echo "   ├── calibracion_20251015_215630.json"
echo "   ├── README.md"
echo "   ├── requirements.txt"
echo "   ├── setup_entorno.sh             (Crear entorno virtual)"
echo "   ├── instalar_dependencias.sh     (Instalar paquetes)"
echo "   ├── ejecutar_sistema.sh          (Ejecutar programa)"
echo "   ├── capturas_estatura/           (Fotos capturadas)"
echo "   ├── resultados_predicciones/     (Resultados JSON)"
echo "   ├── images/                      (Recursos)"
echo "   └── models/                      (Modelos adicionales)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Ejecuta: ./setup_entorno.sh"
echo "   2. Ejecuta: ./instalar_dependencias.sh"
echo "   3. Ejecuta: ./ejecutar_sistema.sh"
echo ""
