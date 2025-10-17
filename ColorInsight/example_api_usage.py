"""
Ejemplo de cómo enviar imágenes a la API de ColorInsight
"""
import requests
import base64
import json


def enviar_imagen_skin_tone(ruta_imagen: str, api_url: str = "http://localhost:8000/image"):
    """
    Envía una imagen para análisis de tono de piel (personal color)
    
    Args:
        ruta_imagen: Ruta al archivo de imagen (jpg, png, etc.)
        api_url: URL del endpoint (default: http://localhost:8000/image)
    
    Returns:
        Respuesta de la API
    """
    # Leer la imagen y convertirla a base64
    with open(ruta_imagen, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Formatear como data URL (similar a lo que enviaría un navegador)
    image_base64 = f"data:image/jpeg;base64,{image_data}"
    
    # Preparar el payload
    payload = {
        "image": image_base64
    }
    
    # Enviar la solicitud POST
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        print(f"✅ Respuesta exitosa: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Detalles: {e.response.text}")
        return None


def enviar_imagen_lip_color(ruta_imagen: str, api_url: str = "http://localhost:8000/lip"):
    """
    Envía una imagen para análisis de color de labios
    
    Args:
        ruta_imagen: Ruta al archivo de imagen (jpg, png, etc.)
        api_url: URL del endpoint (default: http://localhost:8000/lip)
    
    Returns:
        Respuesta de la API
    """
    # Leer la imagen y convertirla a base64
    with open(ruta_imagen, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Formatear como data URL
    image_base64 = f"data:image/jpeg;base64,{image_data}"
    
    # Preparar el payload
    payload = {
        "image": image_base64
    }
    
    # Enviar la solicitud POST
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        print(f"✅ Respuesta exitosa: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Detalles: {e.response.text}")
        return None


# Ejemplo de uso
if __name__ == "__main__":
    # Reemplaza con la ruta a tu imagen
    ruta_a_tu_imagen = "r5.png"
    
    print("=" * 50)
    print("Analizando tono de piel (personal color)...")
    print("=" * 50)
    resultado_skin = enviar_imagen_skin_tone(ruta_a_tu_imagen)
    
    if resultado_skin:
        print("\n📊 Resultado del Análisis de Tono de Piel:")
        print(f"   Temporada: {resultado_skin.get('season')}")
        print(f"   Código: {resultado_skin.get('result')}")
        print(f"   Estado: {resultado_skin.get('message')}")
        print("\n   Significado de las temporadas:")
        print("   - Spring (Primavera): Tonos cálidos y brillantes")
        print("   - Summer (Verano): Tonos fríos y suaves")
        print("   - Autumn (Otoño): Tonos cálidos y profundos")
        print("   - Winter (Invierno): Tonos fríos y intensos")
    
    print("\n" + "=" * 50)
    print("Analizando color de labios...")
    print("=" * 50)
    resultado_lip = enviar_imagen_lip_color(ruta_a_tu_imagen)
    
    if resultado_lip:
        print("\n📊 Resultado del Análisis de Color de Labios:")
        print(f"   Temporada: {resultado_lip.get('season')}")
        print(f"   Código: {resultado_lip.get('result')}")
        print(f"   Tipo: {resultado_lip.get('analysis_type')}")
        print(f"   Estado: {resultado_lip.get('message')}")
