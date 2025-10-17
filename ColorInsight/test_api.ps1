# Script de prueba para la API usando PowerShell

# Ruta a tu imagen
$imagePath = "tu_foto.jpg"

# Convertir imagen a Base64
$imageBytes = [System.IO.File]::ReadAllBytes($imagePath)
$imageBase64 = [System.Convert]::ToBase64String($imageBytes)
$imageDataUrl = "data:image/jpeg;base64,$imageBase64"

Write-Host "======================================"
Write-Host "Testing /image endpoint (Skin Tone)..."
Write-Host "======================================"

# Crear el objeto JSON
$body = @{
    image = $imageDataUrl
} | ConvertTo-Json

# Enviar solicitud al endpoint /image
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/image" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "✅ Respuesta exitosa:"
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n"
Write-Host "======================================"
Write-Host "Testing /lip endpoint (Lip Color)..."
Write-Host "======================================"

# Enviar solicitud al endpoint /lip
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/lip" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "✅ Respuesta exitosa:"
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n"
Write-Host "Nota: Los resultados reales se envían a http://localhost:3000/"
Write-Host "  - /image -> http://localhost:3000/output"
Write-Host "  - /lip -> http://localhost:3000/output2"
