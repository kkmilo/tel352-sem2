import fastapi
import functions as f
import cv2
from PIL import Image
from collections import Counter
import numpy as np
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile
import base64
import skin_model as m
import requests
            

app = FastAPI()

origins = [
    "http://localhost:3000"  # 스프링 부트 애플리케이션이 실행 중인 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Endpoint de prueba para verificar que la API está funcionando
    """
    return {
        "message": "ColorInsight API está funcionando",
        "version": "1.0",
        "endpoints": {
            "/image": "POST - Analiza tono de piel (Personal Color)",
            "/lip": "POST - Analiza color de labios",
            "/docs": "GET - Documentación interactiva"
        }
    }

@app.post("/image")
async def image(data: dict):
    """
    Analiza el tono de piel y determina el tipo de color personal
    Retorna: 1=Spring, 2=Summer, 3=Autumn, 4=Winter
    """
    try:
        image_data = data["image"]
        decoded_image = base64.b64decode(image_data.split(",")[1])

        with open("saved.jpg","wb") as fi:
            fi.write(decoded_image)
      
        f.save_skin_mask("saved.jpg")
   
        ans = m.get_season("temp.jpg")
        os.remove("temp.jpg")
        os.remove("saved.jpg")
   
        if ans == 3:
            ans += 1
        elif ans == 0:
            ans = 3

        # Mapear el resultado a nombres de temporadas
        season_names = {1: "Spring", 2: "Summer", 3: "Autumn", 4: "Winter"}
        
        result_data = {
            'result': ans,
            'season': season_names.get(ans, "Unknown"),
            'message': 'complete'
        }
        
        # Intentar enviar al servidor Spring Boot si está disponible
        try:
            test = {'result': ans}
            encoded_data = base64.b64encode(str(test).encode('utf-8')).decode('utf-8')
            requests.post('http://localhost:3000/output', json={'encodedData':encoded_data}, timeout=1)
        except:
            # Si el servidor Spring Boot no está disponible, simplemente continuar
            pass
        
        return JSONResponse(content=result_data)
        
    except Exception as e:
        import traceback
        error_detail = f"Error processing image: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lip")
async def lip(data: dict):
    """
    Analiza el color de labios y determina el tipo de paleta
    Retorna: 1=Spring, 2=Summer, 3=Autumn, 4=Winter
    """
    try:
        image_data = data["image"]
        decoded_image = base64.b64decode(image_data.split(",")[1])
       
        with open("saved.jpg","wb") as fi:
            fi.write(decoded_image)
        
        path = r"saved.jpg"
       
        rgb_codes = f.get_rgb_codes(path)  #check point
     
        random_rgb_codes = f.filter_lip_random(rgb_codes,40) #set number of randomly picked sample as 40

        os.remove("saved.jpg")
     
        types = Counter(f.calc_dis(random_rgb_codes))
    
        max_value_key = max(types, key=types.get)
        print(f"Lip color analysis result: {max_value_key}")
        
        if max_value_key == 'sp':
            result = 1
        elif max_value_key == 'su':
            result = 2
        elif max_value_key == 'au':
            result = 3
        elif max_value_key == 'win':
            result = 4
        else:
            result = 0
        
        # Mapear el resultado a nombres de temporadas
        season_names = {1: "Spring", 2: "Summer", 3: "Autumn", 4: "Winter"}
        
        result_data = {
            'result': result,
            'season': season_names.get(result, "Unknown"),
            'analysis_type': max_value_key,
            'message': 'complete'
        }
        
        # Intentar enviar al servidor Spring Boot si está disponible
        try:
            data_to_send = {'image': image_data, 'result': result}
            encoded_data = base64.b64encode(str(data_to_send).encode('utf-8')).decode('utf-8')        
            requests.post("http://localhost:3000/output2", json={'encodedData':encoded_data}, timeout=1)
        except:
            # Si el servidor Spring Boot no está disponible, simplemente continuar
            pass
        
        return JSONResponse(content=result_data)
    except Exception as e:
        import traceback
        error_detail = f"Error processing lip image: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))

