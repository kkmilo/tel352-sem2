# 🎨 ColorInsight - Guía Rápida de Uso

## 🚀 Inicio Rápido

### Opción 1: Uso Local (Recomendado para análisis individual)

```powershell
# Análisis completo
python colorInsight.py "C:/ruta/a/tu/foto.jpg"

# Solo tono de piel
python colorInsight.py "C:/ruta/a/tu/foto.jpg" --skin

# Solo color de labios
python colorInsight.py "C:/ruta/a/tu/foto.jpg" --lip
```

### Opción 2: Procesamiento por Lotes

```powershell
# Procesar todas las imágenes de una carpeta
python procesar_lote.py "C:/ruta/a/carpeta/con/fotos/"

# Genera un archivo resultados.json con todos los análisis
```

### Opción 3: Uso con API (para integración web)

```powershell
# 1. Iniciar servidor
.\.venv\Scripts\activate
uvicorn main:app --reload

# 2. Usar desde Python
python example_api_usage.py

# 3. O con PowerShell
.\test_api.ps1
```

## 📋 Formatos de Entrada

**Imágenes soportadas:**
- JPG/JPEG
- PNG
- BMP
- GIF

**Requisitos de la imagen:**
- Debe contener un rostro visible
- Buena iluminación
- Rostro frontal o semi-frontal
- Resolución mínima: 224x224px (recomendado)

## 📊 Interpretación de Resultados

### Códigos de Temporada
- **1 = Spring (Primavera)**: Tonos cálidos y brillantes
- **2 = Summer (Verano)**: Tonos fríos y suaves
- **3 = Autumn (Otoño)**: Tonos cálidos y profundos
- **4 = Winter (Invierno)**: Tonos fríos e intensos

### Paletas de Colores Recomendadas

#### 🌸 Spring (Primavera)
- Colores: Coral, melocotón, dorado, verde lima, turquesa claro
- Maquillaje: Labiales coral, sombras doradas, rubores melocotón
- Ropa: Tonos claros y brillantes, evitar negro puro

#### 🌊 Summer (Verano)
- Colores: Lavanda, rosa pálido, azul suave, gris perla, verde menta
- Maquillaje: Labiales rosa, sombras plateadas, rubores rosados
- Ropa: Tonos pastel y apagados, evitar colores muy saturados

#### 🍂 Autumn (Otoño)
- Colores: Terracota, verde oliva, camel, mostaza, marrón chocolate
- Maquillaje: Labiales terracota, sombras cobre, rubores bronce
- Ropa: Tonos tierra y cálidos, evitar colores muy brillantes

#### ❄️ Winter (Invierno)
- Colores: Negro, blanco puro, rojo intenso, azul royal, fucsia
- Maquillaje: Labiales rojos puros, sombras plateadas, rubores fucsia
- Ropa: Colores puros y contrastantes, evitar tonos apagados

## 🛠️ Solución de Problemas

### Error: "No module named 'matplotlib'"
```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Archivo no encontrado"
- Verifica que la ruta sea correcta
- Usa comillas si la ruta tiene espacios: `"C:/Mi Carpeta/foto.jpg"`
- En Windows, usa `/` o `\\` en las rutas

### Error: "No se detectó ningún rostro"
- Asegúrate de que la imagen contenga un rostro visible
- Mejora la iluminación de la foto
- Usa una foto frontal o semi-frontal

### El servidor no inicia
```powershell
# Verificar que el puerto 8000 no esté ocupado
netstat -ano | findstr :8000

# Usar otro puerto
uvicorn main:app --reload --port 8001
```

## 📁 Estructura de Archivos

```
ColorInsight/
├── colorInsight.py          # Script principal (uso local)
├── procesar_lote.py         # Procesamiento de múltiples imágenes
├── main.py                  # Servidor API
├── functions.py             # Funciones de procesamiento
├── skin_model.py            # Modelo de deep learning
├── example_api_usage.py     # Ejemplos de uso de API
├── requirements.txt         # Dependencias
└── best_model_resnet_ALL.pth # Modelo entrenado
```

## 💡 Tips y Mejores Prácticas

1. **Para mejores resultados:**
   - Usa fotos con buena iluminación natural
   - Evita filtros o efectos en la imagen
   - El rostro debe ocupar al menos 30% de la imagen

2. **Procesamiento rápido:**
   - Usa el script local en lugar de la API
   - Para muchas imágenes, usa `procesar_lote.py`

3. **Integración con otras aplicaciones:**
   - Usa la API REST para integrar con web apps
   - Los resultados en JSON son fáciles de procesar

## 🆘 Ayuda

Para más información:
```powershell
python colorInsight.py --help
```

Para ver documentación de la API:
- Inicia el servidor
- Visita: http://localhost:8000/docs
