# ColorInsight API

API REST para análisis de colorimetría personal (piel, pelo, labios).

## Instalación

```bash
pip install fastapi uvicorn opencv-python pillow numpy
```

## Ejecutar

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### POST `/analyze/color`

Analiza colores de una imagen facial.

**Parámetros:**
- `image`: Archivo de imagen (multipart/form-data)
- `method`: Método de segmentación (query param)
  - `simple`: Haar Cascades (por defecto, rápido)
  - `mediapipe`: MediaPipe (requiere mediapipe instalado)
  - `facer_tflite`: BiSeNet (experimental)

**Ejemplo de uso:**

```bash
curl -X POST "http://localhost:8000/analyze/color?method=simple" \
  -F "image=@foto.jpg"
```

**Respuesta:**

```json
{
  "status": "success",
  "method": "simple",
  "analysis": {
    "Piel": {
      "season": "Summer (Verano)",
      "description": "Tonos fríos y suaves"
    },
    "Pelo": {
      "season": "Winter (Invierno)",
      "description": "Tonos fríos e intensos"
    },
    "Labios": {
      "season": "Summer (Verano)",
      "description": "Tonos fríos y suaves"
    }
  },
  "masks": {
    "Piel": "base64_encoded_image...",
    "Pelo": "base64_encoded_image...",
    "Labios": "base64_encoded_image..."
  }
}
```

## Docs Interactiva

Abre en tu navegador: `http://localhost:8000/docs`
