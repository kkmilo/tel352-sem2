# Sistema de Captura y Predicción de Estatura

Sistema de visión por computadora para medir la estatura de personas usando una cámara web.

## 🚀 Instalación Rápida (3 pasos)

### 1. Crear entorno virtual
```bash
chmod +x setup_entorno.sh
./setup_entorno.sh
```

### 2. Instalar dependencias
```bash
chmod +x instalar_dependencias.sh
./instalar_dependencias.sh
```

### 3. Ejecutar el sistema
```bash
chmod +x ejecutar_sistema.sh
./ejecutar_sistema.sh
```

## 📋 Requisitos del Sistema

- **Sistema Operativo:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.8 o superior
- **Cámara Web:** Cualquier cámara compatible con OpenCV
- **Espacio:** ~100 MB para dependencias

## 🎯 ¿Qué hace el sistema?

1. **Captura de fotos:** Usa tu cámara web para tomar fotos de personas
2. **Detección de pose:** Usa MediaPipe para detectar puntos clave del cuerpo
3. **Predicción de altura:** Modelo Random Forest entrenado con 4,000 personas
4. **Calibración aplicada:** Corrección de +8.78 cm para mayor precisión
5. **Resultados:** Muestra altura estimada con interfaz gráfica

## 📊 Precisión del Modelo

- **MAE (Error Absoluto Medio):** 5.15 cm (modelo base)
- **Con calibración:** 0.41 cm (error promedio)
- **88.1%** de predicciones con error < 10 cm
- **56%** de predicciones con error < 5 cm

## 📁 Estructura del Proyecto

```
.
├── captura_y_prediccion.py                    # Programa principal
├── modelo_altura_random_forest_*.pkl          # Modelo entrenado (8.6 MB)
├── scaler_*.pkl                               # Normalizador de datos
├── modelo_metadata_*.json                     # Información del modelo
├── calibracion_*.json                         # Calibración aplicada
├── haarcascade_frontalface_default.xml        # Detector de rostros
├── requirements.txt                           # Dependencias Python
├── setup_entorno.sh                           # Script 1: Crear entorno
├── instalar_dependencias.sh                   # Script 2: Instalar paquetes
├── ejecutar_sistema.sh                        # Script 3: Ejecutar programa
├── capturas_estatura/                         # Fotos capturadas
└── resultados_predicciones/                   # Resultados JSON
```

## 🔧 Uso del Sistema

### Interfaz Gráfica

Al ejecutar el sistema verás:

- **Vista de cámara en vivo:** Previsualización con detección de pose
- **Indicador de distancia:** Verifica que la persona esté a 2.5m
- **Botón "Capturar":** Toma la foto y predice altura
- **Resultados:** Altura estimada en cm
- **Historial:** Últimas predicciones realizadas

### Recomendaciones para mejores resultados

1. **Distancia:** Coloca a la persona a 2.5 metros de la cámara
2. **Iluminación:** Ambiente bien iluminado, luz frontal o superior
3. **Postura:** Persona de pie, brazos a los costados, de frente a la cámara
4. **Fondo:** Fondo uniforme sin obstáculos
5. **Ropa:** Ropa ajustada facilita la detección de pose

## 📦 Dependencias

```
opencv-python>=4.8.0      # Procesamiento de imágenes y cámara
mediapipe>=0.10.0         # Detección de pose
numpy>=1.24.0             # Cálculos numéricos
pillow>=10.0.0            # Manejo de imágenes
joblib>=1.3.0             # Carga del modelo
scikit-learn>=1.3.0       # Modelo de predicción
```

## 🐛 Solución de Problemas

### Error: "No se pudo acceder a la cámara"
```bash
# Verificar cámaras disponibles
ls /dev/video*

# Dar permisos
sudo chmod 666 /dev/video0
```

### Error: "No se encontró el modelo"
Verifica que existan estos archivos:
```bash
ls -lh modelo_altura_random_forest_*.pkl
ls -lh scaler_*.pkl
ls -lh calibracion_*.json
```

### Error: "ModuleNotFoundError"
Reinstala las dependencias:
```bash
./instalar_dependencias.sh
```

## 🧪 Especificaciones Técnicas

### Modelo
- **Tipo:** Random Forest Regressor
- **Árboles:** 100
- **Profundidad máxima:** 20
- **Muestras de entrenamiento:** 4,000
- **Features:** 15 características de pose

### Calibración
- **Método:** Offset aditivo
- **Corrección:** +8.78 cm
- **Basado en:** 10 fotos de calibración
- **MAE post-calibración:** 0.41 cm

### Características Detectadas
1. Distancia nariz-tobillo (píxeles)
2. Proporción pierna/torso
3. Proporción altura/ancho
4. Ancho de hombros relativo
5. Longitud de muslo
6. Altura de imagen
7. Ancho de imagen
8. Confianza promedio de detección
9-15. Visibilidad de puntos clave

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y de investigación.

## 👤 Autor

Sistema desarrollado para Seminario II - 2025

## 📞 Soporte

Para problemas o preguntas, revisa los archivos de log en:
- `capturas_estatura/` - Fotos capturadas
- `resultados_predicciones/` - Resultados en formato JSON

---

**Versión:** 1.0.0 (Modelo entrenado: 15/10/2025)
