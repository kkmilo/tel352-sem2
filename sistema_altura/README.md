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
│   ├── modelo_*.pkl              # Modelo Random Forest
│   ├── scaler_*.pkl              # Normalizador
│   ├── modelo_metadata_*.json    # Metadata del modelo
│   └── calibracion_*.json        # Calibración aplicada
├── scripts/                      # Scripts de configuración
│   ├── setup_entorno.sh          # Crear entorno virtual
│   ├── instalar_dependencias.sh  # Instalar paquetes
│   ├── ejecutar_sistema.sh       # Ejecutar el sistema
│   └── inicio_rapido.sh          # Instalación automática
├── config/                       # Archivos de configuración
│   └── haarcascade_*.xml         # Detector de rostros
├── data/                         # Datos del usuario
│   ├── capturas/                 # Fotos capturadas
│   └── resultados/               # Resultados JSON
├── docs/                         # Documentación
│   ├── README.md                 # Documentación completa
│   └── INSTRUCCIONES_FINALES.txt # Guía de uso
├── venv/                         # Entorno virtual (se crea)
└── requirements.txt              # Dependencias Python
```

## 📊 Características

- **Precisión:** MAE 5.15 cm (base), 0.41 cm (con calibración)
- **Modelo:** Random Forest con 4,000 muestras
- **Detección:** MediaPipe Pose Detection
- **Interfaz:** GUI con Tkinter

## 🔧 Requisitos

- Python 3.8+
- Cámara web
- Linux (Ubuntu/Debian recomendado)

## 📖 Documentación Completa

Ver `docs/README.md` para documentación detallada.
