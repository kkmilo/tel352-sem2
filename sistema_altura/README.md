# Sistema de Captura y Predicción de Estatura

## 🚀 Inicio Rápido

### Instalación Automática (Recomendado)

```bash
cd sistema_altura
./scripts/inicio_rapido.sh
```

### Instalación Manual

```bash
cd sistema_altura

# 1. Crear entorno virtual
./scripts/setup_entorno.sh

# 2. Instalar dependencias
./scripts/instalar_dependencias.sh

# 3. Ejecutar sistema
./scripts/ejecutar_sistema.sh
```

## 📁 Estructura del Proyecto

```
sistema_altura/
├── app/                          # Aplicación principal
│   └── captura_y_prediccion.py   # Programa principal
├── modelos/                      # Modelos entrenados
│   ├── modelo_altura_*.tflite    # Modelo TFLite para inferencia
│   ├── scaler_*.pkl              # Normalizador
│   ├── modelo_metadata_*.json    # Metadata del modelo
│   └── calibracion_*.json        # Calibración aplicada
├── scripts/                      # Scripts de configuración y utilidades
│   ├── setup_entorno.sh          # Crear entorno virtual
│   ├── instalar_dependencias.sh  # Instalar paquetes
│   ├── ejecutar_sistema.sh       # Ejecutar el sistema (GUI)
│   ├── inicio_rapido.sh          # Instalación automática
│   ├── limpiar_proyecto.sh       # Limpieza de artefactos antiguos
│   ├── predicciones_headless.py  # Inferencia sin GUI (por lotes)
│   ├── analizar_offsets.py       # Análisis de calibraciones/resultados
│   ├── entrenar_dnn_altura.py    # (Opcional) Entrenamiento DNN
│   └── generar_dataset_sintetico.py # (Opcional) Datos sintéticos
├── config/                       # Archivos de configuración
│   └── haarcascade_*.xml         # Detector de rostros
├── capturas_estatura/            # Fotos capturadas (recientes)
├── resultados_predicciones/      # Resultados JSON/imagenes
├── docs/                         # Documentación
│   ├── README.md                 # Documentación completa
│   └── INSTRUCCIONES_FINALES.txt # Guía de uso
├── venv/                         # Entorno virtual (se crea)
└── requirements.txt              # Dependencias Python
```

## 📊 Características

- Precisión: MAE ~5.6 cm (modelo DNN TFLite en dataset de prueba sintético)
- Modelo: DNN convertido a TensorFlow Lite con 15 características (features de pose)
- Detección: MediaPipe Pose
- Interfaz: GUI con Tkinter, cámara se enciende automáticamente
- Auto-captura: si la calidad de detección es “EXCELENTE”, se dispara una captura con cuenta regresiva de 3 segundos
- Calibración: ajuste por offset aditivo contra tu estatura real; se persiste en `modelos/calibracion_*.json`
- Resultados: se guardan altura sin calibración (`altura_sin_calibracion_cm`) y calibrada (`altura_predicha_cm`)
- Headless: script para ejecutar predicciones sin GUI y otro para analizar offsets y estadísticas

## 🧠 Modelos incluidos y datos

- Modelo actual (recomendado):
  - `modelos/modelo_altura_dnn_*.tflite`
  - `modelos/scaler_*.pkl`
  - `modelos/modelo_metadata_*.json`
  - `modelos/calibracion_*.json` (opcional)

- Datos de entrenamiento:
  - Dataset de referencia: ANSUR II (no incluido por tamaño). Se proporciona un dataset sintético y un modelo TFLite ya convertido para ejecución inmediata.

## ⚙️ TensorFlow Lite (TFLite)

La aplicación usa exclusivamente modelos `*.tflite` para la inferencia.

- En Python < 3.12: se instala `tflite-runtime` (ligero, recomendado para inferencia)
- En Python >= 3.12: se usa `tensorflow` y su `tf.lite.Interpreter` (no hay wheel oficial de `tflite-runtime` para 3.12)

Entrenamiento/Conversión (opcional):

- Script: `scripts/entrenar_dnn_altura.py`
- Entrada: CSV con las 15 features + columna `height_cm`
- Salida: `.tflite`, `scaler_*.pkl`, `modelo_metadata_*.json` y opcionalmente `calibracion_*.json`

## 🔧 Requisitos

- Python 3.8+ (3.12 soportado con fallback a TensorFlow)
- Cámara web
- Linux (Ubuntu/Debian recomendado)

## 🖥️ Uso de la GUI

- Inicia el sistema con: `./scripts/ejecutar_sistema.sh`
- La cámara se enciende automáticamente. Sigue las guías en pantalla.
- Cuando la calidad de detección sea “EXCELENTE” y la distancia sea adecuada, comenzará una cuenta regresiva de 3 segundos y se realizará la captura automáticamente.
- Para calibrar: ingresa tu estatura real en la UI. El sistema calculará un offset usando la predicción sin calibración y lo guardará en `modelos/calibracion_*.json`.

## 🧪 Ejecución Headless (sin GUI)

El script `scripts/predicciones_headless.py` ahora soporta 3 modos:

- **Modo cámara** (sin GUI): captura `N` predicciones desde la webcam
  ```bash
  ./venv/bin/python scripts/predicciones_headless.py --num 5 --device 0 --cooldown 1.5
  ```

- **Modo carpeta**: procesa hasta `N` imágenes de una carpeta
  ```bash
  ./venv/bin/python scripts/predicciones_headless.py --images-dir capturas_estatura --num 10
  ```

- **Imagen única**: procesa una sola imagen puntual
  ```bash
  ./venv/bin/python scripts/predicciones_headless.py --image capturas_estatura/mi_foto.jpg
  ```

Salidas y métricas:
- Guarda en `resultados_predicciones/` una imagen anotada `prediccion_headless_*.jpg` y un JSON `prediccion_headless_*.json`.
- El JSON incluye: `altura_predicha_cm` (calibrada), `altura_sin_calibracion_cm` (cruda), `confianza`, `visibilidad_landmarks`, y `caracteristicas` clave.

Notas de uso:
- Extensiones de imagen soportadas: `.jpg`, `.jpeg`, `.png`.
- Para mejores resultados en imágenes estáticas: cuerpo completo visible, distancia ~2 m, luz uniforme, fondo contrastante.

Análisis de calibraciones/offsets:
```bash
./venv/bin/python scripts/analizar_offsets.py
```

## 📖 Documentación Completa

Ver `docs/README.md` para documentación detallada.
