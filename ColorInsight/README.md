### Colorinsight (Personal Color detection model, 퍼스널컬러 진단모델) <br>
https://user-images.githubusercontent.com/86555104/226335673-e7cb3df0-7128-4fcb-9c9e-3c397ecd22f1.mp4
<br> Personal color refers to the colors that look best on an individual based on their skin tone, hair color, and eye color. Personal color analysis is a process that helps identify an individual's personal color palette, which consists of a range of colors that complement their natural features. This concept is used in the fashion and beauty industries to help individuals choose colors for clothing, makeup, and accessories that flatter their appearance. <br>

Our team built the website called 'Colorinsight' because of two big motivations: 1) Current private personal color consulting services have low reliability due to subjective diagnosis compared to high prices. 2) The demand for personalized beauty industry is growing worldwide. Our model is developed based on a thorough research on the existing personal color theories and concrete experiments on deep learning models to make practical service for the users.

### 🚀 Quick Start

#### Prerequisites
- Python 3.8 or higher
- Windows PowerShell (for Windows users)

#### Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ColorInsight
```

2. **Create and activate virtual environment** (PowerShell)
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Run the application**
```powershell
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 💻 Uso Local (Sin API)

Para análisis directo desde la línea de comandos sin necesidad de levantar la API:

```powershell
# Análisis completo (tono de piel + color de labios)
python colorInsight.py "C:/ruta/a/tu/imagen.jpg"

# Solo análisis de tono de piel
python colorInsight.py "C:/ruta/a/tu/imagen.jpg" --skin

# Solo análisis de color de labios
python colorInsight.py "C:/ruta/a/tu/imagen.jpg" --lip
```

**Ventajas del uso local:**
- ✅ No requiere servidor API corriendo
- ✅ Procesamiento más rápido
- ✅ Resultados directos en consola
- ✅ Ideal para procesamiento por lotes

**Ejemplo de salida:**
```
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
   COLORINSIGHT - ANÁLISIS COMPLETO DE COLOR PERSONAL
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

✅ RESULTADO:
   🎯 Temporada: Autumn (Otoño)
   📊 Código: 3
   💡 Descripción: Tonos cálidos y profundos
```

#### API Endpoints
- `POST /image` - Analyze skin tone from uploaded image
- `POST /lip` - Analyze lip color from uploaded image

### 📸 Cómo Usar la API

#### Formato de la Solicitud

Ambos endpoints (`/image` y `/lip`) esperan un JSON con la imagen codificada en Base64:

```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
}
```

#### Ejemplo en Python

```python
import requests
import base64

# Leer y codificar la imagen
with open("tu_foto.jpg", 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# Formatear como data URL
image_base64 = f"data:image/jpeg;base64,{image_data}"

# Enviar a la API
response = requests.post(
    "http://localhost:8000/image",
    json={"image": image_base64}
)

print(response.json())  # {"message": "complete"}
```

#### Ejemplo en PowerShell

```powershell
# Convertir imagen a Base64
$imageBytes = [System.IO.File]::ReadAllBytes("tu_foto.jpg")
$imageBase64 = [System.Convert]::ToBase64String($imageBytes)
$imageDataUrl = "data:image/jpeg;base64,$imageBase64"

# Crear JSON y enviar
$body = @{ image = $imageDataUrl } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/image" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

#### Ejemplo en JavaScript/Fetch

```javascript
// Desde un input file en HTML
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

const reader = new FileReader();
reader.onloadend = async () => {
    const response = await fetch('http://localhost:8000/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: reader.result })
    });
    const data = await response.json();
    console.log(data);
};
reader.readAsDataURL(file);
```

#### Archivos de Ejemplo

El proyecto incluye scripts de ejemplo para probar la API:

- **`example_api_usage.py`** - Script Python con ejemplos completos
- **`test_api.ps1`** - Script PowerShell para Windows
- **`test_api.sh`** - Script Bash para Linux/Mac

Para usar los scripts de prueba:

```powershell
# PowerShell (Windows)
.\test_api.ps1

# Python
python example_api_usage.py
```

#### Resultados

- **`/image`**: Analiza el tono de piel y determina la temporada de color personal
  - Valores: 1=Spring, 2=Summer, 3=Autumn, 4=Winter
  
- **`/lip`**: Analiza el color de labios para determinar la paleta de colores
  - Valores: 1=Spring, 2=Summer, 3=Autumn, 4=Winter

**Nota**: La API envía los resultados a un servidor Spring Boot en `http://localhost:3000/output` o `http://localhost:3000/output2`. El endpoint retorna `{"message": "complete"}` cuando el procesamiento es exitoso.


### ⛏ Model Overview

![image](https://user-images.githubusercontent.com/86555104/226334045-07eddda5-61ac-4446-9bc8-07edeb7090f2.png)
We implemeted two separated models for the personal color diagnosis. After the careful comparison of performance between several models, we selected FaRL model which showed outstanding performance compared to other face segmentation models even in complicated situation(face in different direction, extreme face shape...etc.). After sementing pure skin part of face, we trained another image classification model with Korean celebrity images. The dataset was collected by Google image crawling using python selenium. To overcome the limited image data(750 images), data augmentation was employed. (dataset is not uploaded on a repository for a privacy protection)


### A. Deep Learning Model Backbone (FaRL model)
The backbone of this personal color detection model is based on a face parsing model from FaRL(Facial Representation Learning) from the great authors below.

@article{zheng2021farl,
  title={General Facial Representation Learning in a Visual-Linguistic Manner},
  author={Zheng, Yinglin and Yang, Hao and Zhang, Ting and Bao, Jianmin and Chen, Dongdong and Huang, Yangyu and Yuan, Lu and Chen, Dong and Zeng, Ming and Wen, Fang},
  journal={arXiv preprint arXiv:2112.03109},
  year={2021}
}<br>

### C. Personal Color diagnosis model
After obtaining face skin mask image, we tried three approaches to find the most suitable model that matches an exact personal color type. (Personal color type is divided into four categories: spring, summer, autumnm, winter) First approach was to categorize personal color type with L2 norm distance between particular rgb code data point from the research paper and randomly extracted rgb codes from skin mask area. For the second approach, we made additional structured dataset with r,g,b columns extracted from face skin mask. The, we applied machine learning classification model to predict the proper personal color type label. However, these two methods resulted low accuracy rate ranging from 20% to 30 % with the limitation that it fails to predict 'autumn' type. <br>

As a last attempt , we organized another image dataset that extracted face skin mask image from previously collected Korean celebrity face dataset. Then we tested popular image classification models including MobileNet, ResNet and EfficientNet. ResNet with Adam optimizer demonstrated the best performance among all, that we eventually used this model for the prediction. 
*ResNet was trained in Colab and loaded model via best_model_resnet_ALL.pth file.
![image](https://user-images.githubusercontent.com/86555104/226340188-2cfe2cba-23f5-4112-a51f-cfe9e1c32b12.png)


### Possible Improvements
- It is successful that the accuracy of model is improved from 20% to around 60%, however, additional efforts such as increased training epoch and dataset expansion can improve model's performance.
- Current dataset is based on Korean celebrity photos, but utilizing photos of ordinary people in different angles will enable model to learn realistic human skin color and expand its usage on diverse races.<br>

Detailed experiment reports can be found here(written in Korean) 👉[Deep Learning Model Experiment Reports](https://tar-tilapia-c6d.notion.site/403c8d583e3a4f6bb9f76ea6efd991d5?v=f9b650bea3e144918ec577eb464ddcd5/)
