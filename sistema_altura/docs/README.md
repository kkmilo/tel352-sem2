# Sistema de Captura y Predicción de Estatura

Sistema de visión por computadora para medir la estatura de personas usando una cámara web.

## 🚀 Instalación Rápida (3 pasos)

### 1. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3. Ejecutar el sistema
```bash
python app/captura_y_prediccion.py
```

## 📋 Requisitos del Sistema

- **Sistema Operativo:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.12
- **Cámara Web:** Cualquier cámara compatible con OpenCV
- **Espacio:** ~100 MB para dependencias

## 🎯 ¿Qué hace el sistema?

1. **Auto-encendido de cámara:** La cámara se activa automáticamente al iniciar
2. **Detección de pose:** Usa MediaPipe para detectar puntos clave del cuerpo
3. **Auto-captura inteligente:** Cuando la calidad de detección es "EXCELENTE", inicia cuenta regresiva de 3 segundos y captura automáticamente
4. **Predicción de altura:** Modelo DNN en TensorFlow Lite (TFLite) con 15 características de pose
5. **Calibración:** Ajuste por offset aditivo usando tu estatura real; persiste en `modelos/calibracion_*.json`
6. **Resultados duales:** Muestra altura sin calibración (raw) y calibrada en interfaz gráfica y JSON

## 📊 Precisión del Modelo

- **MAE (Error Absoluto Medio):** ~5.6 cm (modelo DNN TFLite en dataset de prueba sintético)
- **Calibración:** Offset aditivo opcional (+2.20 cm según archivo de calibración)

## 📁 Estructura del Proyecto

```text
.
├── app/
│   └── captura_y_prediccion.py                # Programa principal (GUI + inferencia TFLite)
├── modelos/
│   ├── modelo_altura_dnn_*.tflite             # Modelo TFLite (inferencias)
│   ├── scaler_*.pkl                           # Normalizador de datos (StandardScaler)
│   ├── modelo_metadata_*.json                 # Información del modelo (features, métricas)
│   └── calibracion_*.json                     # Calibración aplicada (offset aditivo)
├── config/
│   └── haarcascade_frontalface_default.xml    # Detector de rostros (opcional)
├── scripts/
│   ├── predicciones_headless.py               # Inferencia sin GUI (por lotes)
│   ├── analizar_offsets.py                    # Análisis de calibraciones/resultados
│   ├── entrenar_dnn_altura.py                 # (Opcional) Entrenamiento DNN
│   └── generar_dataset_sintetico.py           # (Opcional) Datos sintéticos
├── capturas_estatura/                         # Capturas guardadas (auto-creado)
├── resultados_predicciones/                   # Resultados JSON/imágenes
├── venv/                                      # Entorno virtual Python (creado por usuario)
└── requirements.txt                           # Dependencias del proyecto
```

## 🔧 Uso del Sistema

### Interfaz Gráfica

Al ejecutar el sistema verás:

- **Indicadores en pantalla:** Calidad de detección, distancia estimada, guías de posición
- **Auto-captura:** Cuando la calidad es "EXCELENTE" y la distancia es adecuada, inicia cuenta regresiva de 3 segundos y captura automáticamente
- **Vista de cámara en vivo:** Muestra la detección de pose en tiempo real
- **Resultados:** Muestra predicción raw y calibrada

**Controles:**

- `ESC` - Salir del sistema
- `c` - Capturar manualmente (si prefieres no usar auto-captura)
- Botón "Calibrar" - Ingresar tu altura real para ajustar predicciones

### Modo Sin Interfaz (Headless)

Ejecuta predicciones sin GUI usando cámara o imágenes existentes.

Opciones principales:

- `--num`: número de predicciones a generar (por defecto 5)
- `--device`: índice de cámara (por defecto 0)
- `--cooldown`: segundos entre capturas en modo cámara (por defecto 1.5)
- `--images-dir`: carpeta con imágenes `.jpg/.jpeg/.png` a procesar
- `--image`: ruta a una sola imagen a procesar

Ejemplos:

```bash
# Activar entorno
source venv/bin/activate

# 1) Desde cámara (5 predicciones, cámara 0, cooldown 1.5s)
python3 scripts/predicciones_headless.py --num 5 --device 0 --cooldown 1.5

# 2) Procesar una carpeta de imágenes (hasta N)
python3 scripts/predicciones_headless.py --images-dir capturas_estatura --num 10

# 3) Procesar una sola imagen
python3 scripts/predicciones_headless.py --image capturas_estatura/mi_foto.jpg
```

Salidas generadas:

- Carpeta `resultados_predicciones/` con:
  - `prediccion_headless_YYYYMMDD_HHMMSS.jpg`: imagen anotada con landmarks y altura predicha
  - `prediccion_headless_YYYYMMDD_HHMMSS.json`: resultado estructurado con campos clave:
    - `altura_predicha_cm`, `altura_sin_calibracion_cm`, `confianza`, `visibilidad_landmarks`
    - `imagen_original`, `imagen_anotada`, `timestamp`, `fecha`
    - `caracteristicas` (resumen de métricas en píxeles) y `modelo_usado`, `mae_modelo`
- En modo cámara, la imagen original se guarda en `capturas_estatura/` como `captura_headless_*.jpg`.

Notas:

- El script carga automáticamente el modelo TFLite más reciente en `modelos/` junto con su `scaler_*.pkl`, `modelo_metadata_*.json` y, si existe, `calibracion_*.json` (aplica offset aditivo a la salida).
- Si no estás en un entorno virtual, el script mostrará una advertencia. Asegúrate de ejecutar `source venv/bin/activate`.
- Dependencias: `opencv-python`, `mediapipe`, `numpy`, `joblib` y `tflite-runtime` (o `tensorflow>=2.19` como alternativa para Python 3.12+).

Analizar resultados de calibración:

```bash
python3 scripts/analizar_offsets.py
```

### Recomendaciones para mejores resultados

1. **Distancia:** Coloca a la persona a 2.1 metros de la cámara
2. **Iluminación:** Ambiente bien iluminado, luz frontal o superior
3. **Postura:** Persona de pie, brazos a los costados, de frente a la cámara
4. **Fondo:** Fondo uniforme sin obstáculos
5. **Ropa:** Ropa ajustada facilita la detección de pose

## 📦 Dependencias

```text
# Core
opencv-python>=4.8.0      # Procesamiento de imágenes y cámara
mediapipe>=0.9.0          # Detección de pose
numpy>=1.26.0,<2.2.0      # Cálculos numéricos
pillow>=10.0.0            # Manejo de imágenes
joblib>=1.3.0             # Carga del scaler
scikit-learn>=1.3.0       # StandardScaler

# TensorFlow Lite (según versión Python)
tflite-runtime>=2.14.0; python_version < "3.12"        # Liviano (recomendado)
tensorflow>=2.19.0,<2.20.0; python_version >= "3.12"   # Fallback (Python 3.12+)
protobuf>=4.25.3,<5; python_version >= "3.12"          # Compatibilidad TF
```

Instala con:
```bash
pip install -r requirements.txt
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

Verifica que existan estos archivos (en `modelos/`):

```bash
ls -lh modelos/modelo_altura_*.tflite
ls -lh modelos/scaler_*.pkl
ls -lh modelos/modelo_metadata_*.json
ls -lh modelos/calibracion_*.json  # opcional
```

### Error: "ModuleNotFoundError: No module named 'mediapipe'" (o cualquier otro paquete)

**Causa**: El script se ejecuta fuera del entorno virtual o las dependencias no están instaladas.

**Solución**:

1) **Verificar activación del entorno virtual**:

```bash
source venv/bin/activate
which python  # Debe mostrar la ruta al Python del venv
```

2) **Reinstalar dependencias**:

```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

3) **Para Python 3.12+ (si falla mediapipe o TFLite)**:

```bash
pip install --upgrade tensorflow protobuf
pip install --force-reinstall mediapipe opencv-python
```

4) **Verificar instalación**:

```bash
python -c "import cv2, mediapipe, numpy, PIL, joblib, sklearn; print('✓ Todas las dependencias disponibles')"
```

### Error: "ValueError: El modelo predijo X cm, fuera del rango esperado"

**Causa**: La predicción está fuera del rango físicamente plausible (normalmente 100-220 cm).

**Solución**:

- **Recalibra el modelo**: Ejecuta el modo calibración con una persona de altura conocida.
- **Verifica la distancia**: Asegúrate de estar a ~2 metros de la cámara.
- **Iluminación**: Evita contraluces o sombras fuertes en el rostro.
- Si persiste, puede ser necesario reentrenar el modelo con más datos.

### Warning: "numpy.dtype size changed"

**Causa**: Incompatibilidad entre versiones de NumPy y scikit-learn.

**Solución**:

```bash
source venv/bin/activate
pip install --upgrade numpy scikit-learn
```

## 🧪 Especificaciones Técnicas

### Modelo

- **Tipo:** Red Densa (DNN) convertida a TensorFlow Lite
- **Capas:** 256 → 128 → 64 (con dropout)
- **Muestras de entrenamiento:** 4,000 (dataset sintético basado en ANSUR II)
- **Features:** 15 características de pose

Nota sobre datos de entrenamiento:

- El dataset de referencia es ANSUR II (no incluido por tamaño). Para facilitar pruebas, se incluye un dataset sintético en `data/altura_features_sintetico.csv` y un modelo TFLite ya convertido con su `scaler_*.pkl` y `modelo_metadata_*.json`.

### Arquitectura: TensorFlow Lite (TFLite)

La aplicación usa exclusivamente modelos en formato TFLite (`.tflite`) para la predicción. Carga automáticamente el archivo más reciente en `modelos/` y usa `tflite-runtime` para la inferencia.

Para entrenar/convertir un modelo TFLite basado en las 15 features, puedes usar (opcional):

- `scripts/entrenar_dnn_altura.py` si dispones del script de entrenamiento (requiere `tensorflow`)
- Entrada: CSV con columna objetivo `height_cm` y las 15 features
- Salida: `modelo_altura_dnn_*.tflite`, `scaler_*.pkl`, `modelo_metadata_*.json`

### Calibración

- Método: Offset aditivo (se suma a la salida del modelo)
- Archivo: `calibracion_*.json` junto al modelo
- Botón en la app: "Calibrar (ingresar altura real)"

Calibración práctica (recomendada):

1) Realiza una captura para obtener una predicción.
2) Presiona el botón "Calibrar" e ingresa tu altura real (por ejemplo 170).
3) El sistema calcula y guarda un offset para alinear futuras predicciones.
4) Repite si cambias de cámara/escena o si notas un desvío sistemático.

Consejos de ajuste fino:

- Si después de calibrar ves que sobra o falta ±X cm, realiza otra captura y vuelve a pulsar "Calibrar" con tu altura real. El sistema recalcula el offset usando la altura sin calibración más reciente, corrigiendo el sesgo.
- Para reducir el ruido, puedes hacer 2–3 capturas y calibrar con el promedio de tu altura real (o repetir la calibración tras varias capturas similares).
- Avanzado: Puedes editar manualmente el archivo `modelos/calibracion_*.json` y ajustar `offset_aditivo` (en cm). Hazlo con el sistema cerrado y conserva el formato JSON.


### Características Detectadas

Estas son las 15 features que se extraen y alimentan al modelo, en el mismo orden:

1. Altura corporal en píxeles (nariz→tobillos)
2. Longitud de pierna en píxeles (caderas→tobillos)
3. Longitud de torso en píxeles (hombros→caderas)
4. Ancho de hombros en píxeles
5. Ancho de caderas en píxeles
6. Proporción pierna/torso
7. Proporción altura/ancho (altura corporal px / ancho hombros px)
8. Ancho de imagen (px)
9. Alto de imagen (px)
10. Confianza promedio de landmarks
11. Visibilidad nariz
12. Visibilidad hombro izquierdo
13. Visibilidad hombro derecho
14. Visibilidad cadera izquierda
15. Visibilidad cadera derecha

En los resultados JSON se publica un resumen de características con un subconjunto:

- `body_height_px`, `leg_length_px`, `torso_length_px`, `shoulder_width_px`, `hip_width_px`

Ejemplo:

```json
{
  "caracteristicas": {
    "body_height_px": 361.77,
    "leg_length_px": 166.72,
    "torso_length_px": 148.11,
    "shoulder_width_px": 94.0,
    "hip_width_px": 52.96
  }
}
```

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y de investigación.


## 📞 Soporte

Para problemas o preguntas, revisa los archivos de log en:

- `capturas_estatura/` - Fotos capturadas
- `resultados_predicciones/` - Resultados en formato JSON

---

**Versión:** 1.0.0 (Modelo entrenado: 15/10/2025)
