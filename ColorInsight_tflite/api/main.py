from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import cv2
import numpy as np
import base64

from colorinsight_wrapper import run_colorinsight_from_image

app = FastAPI(title="ColorInsight API", version="1.0.0")


@app.get("/")
async def root():
    return {"service": "ColorInsight API", "status": "active"}


@app.post("/analyze/color")
async def analyze_color(
    image: UploadFile = File(...),
    method: str = "simple"
):
    """
    Analiza colores de piel, pelo y labios de una imagen.
    
    Methods:
    - simple: Haar Cascades (rápido, básico)
    - mediapipe: MediaPipe ML (preciso, requiere mediapipe)
    - facer_tflite: BiSeNet model (más preciso, experimental)
    """
    
    if method not in ["simple", "mediapipe", "facer_tflite"]:
        raise HTTPException(
            status_code=400, 
            detail="Method must be 'simple', 'mediapipe', or 'facer_tflite'"
        )
    
    try:
        # Read and process image
        img_bytes = await image.read()
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Run ColorInsight analysis
        analysis = run_colorinsight_from_image(pil_img, method=method, verbose=False)
        
        # Encode masks as base64
        encoded_masks = {}
        for feature, mask_img in analysis["masks"].items():
            _, buffer = cv2.imencode(".jpg", mask_img)
            encoded_masks[feature] = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse(content={
            "status": "success",
            "method": method,
            "analysis": analysis["results"],
            "masks": encoded_masks
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
