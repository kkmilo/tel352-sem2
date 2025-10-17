#!/bin/bash
# Script de prueba para la API usando curl
# Para Windows PowerShell, ver test_api.ps1

# Endpoint de análisis de tono de piel
echo "Testing /image endpoint..."

# Convertir imagen a base64 y enviar
IMAGE_BASE64=$(base64 -w 0 tu_foto.jpg)

curl -X POST "http://localhost:8000/image" \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"data:image/jpeg;base64,$IMAGE_BASE64\"}"

echo -e "\n\n"

# Endpoint de análisis de labios
echo "Testing /lip endpoint..."

curl -X POST "http://localhost:8000/lip" \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"data:image/jpeg;base64,$IMAGE_BASE64\"}"

echo -e "\n"
