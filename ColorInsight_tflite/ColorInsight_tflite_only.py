#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ColorInsight - Versión TFLite Only (Agnóstica a PyTorch)
Requisitos:
  - tflite_runtime (o tensorflow)
  - mediapipe
  - numpy
  - opencv-python
  - requests (para descargar modelos)
"""

import sys
import os
import argparse
import time
import urllib.request

# Force CPU usage to avoid EGL/GPU driver issues on Linux/Raspberry
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# Disable GPU for MediaPipe specifically
os.environ["MEDIAPIPE_GPU_DISABLED"] = "1"
# Fix for EGL crash on Linux (Headless/NVIDIA conflicts)
os.environ["EGL_PLATFORM"] = "surfaceless"

import cv2
import numpy as np
from PIL import Image

# --- Importaciones Condicionales ---

# 1. TFLite Runtime (Prefer full TensorFlow for Flex Ops support)
try:
    import tensorflow.lite as tflite
    # Intentar cargar delegados Flex si es necesario
    # os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        print("❌ Error Crítico: No se encontró 'tensorflow' ni 'tflite_runtime'.")
        print("   Instala: pip install tensorflow (recomendado) o tflite-runtime")
        sys.exit(1)

# 2. MediaPipe (Opcional - solo para método 'mediapipe')
MEDIAPIPE_AVAILABLE = False
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    mp = None
    print("⚠️ MediaPipe no disponible. Solo se podrá usar --method simple")

# 3. TQDM (Opcional)
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs): return iterable

# --- Configuración ---
#MODEL_DIR = "modelos_tflite"
MODEL_DIR = "/home/yohanns/ColorInsight_Pruebas/modelos_tflite/"
RESNET_MODEL_NAME = "resnet18_4clases.tflite"
HAIR_MODEL_NAME = "hair_segmentation.tflite"
FACER_MODEL_NAME = "face_parsing_farl.tflite" # Nuevo modelo convertido

# URLs oficiales o de respaldo
HAIR_MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/hair_segmentation.tflite"

SEASON_NAMES = {
    1: "Spring (Primavera)",
    2: "Summer (Verano)", 
    3: "Autumn (Otoño)",
    4: "Winter (Invierno)"
}

SEASON_DESCRIPTIONS = {
    1: "Tonos cálidos y brillantes",
    2: "Tonos fríos y suaves",
    3: "Tonos cálidos y profundos",
    4: "Tonos fríos e intensos"
}

# --- Funciones de Utilidad ---

def ensure_directory():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"📁 Carpeta creada: {MODEL_DIR}")

def download_file(url, dest_path):
    print(f"⬇️ Descargando {os.path.basename(dest_path)}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("✅ Descarga completada.")
        return True
    except Exception as e:
        print(f"❌ Error descargando: {e}")
        return False

def get_model_path(model_name, url=None):
    ensure_directory()
    path = os.path.join(MODEL_DIR, model_name)
    
    if not os.path.exists(path):
        if url:
            success = download_file(url, path)
            if not success:
                raise FileNotFoundError(f"No se pudo obtener {model_name}")
        else:
            # Buscar en directorio actual como fallback
            local_path = model_name
            if os.path.exists(local_path):
                import shutil
                shutil.copy(local_path, path)
                print(f"🔄 Modelo copiado desde directorio actual: {model_name}")
            else:
                raise FileNotFoundError(f"Modelo no encontrado: {path}")
    return path

def map_model_output(ans):
    # Mapeo específico de tu modelo ResNet entrenado
    if ans == 3: return 4
    elif ans == 0: return 3
    return ans

# --- Inferencia TFLite (Clasificación) ---
def predict_season_tflite(img_path, model_path):
    """
    Versión corregida para evitar errores de dimensiones (input_channel != 0).
    Se asegura de que la entrada coincida exactamente con lo que pide el modelo.
    """
    # 1. Cargar Intérprete
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Obtener la forma EXACTA que pide el modelo (Ej: [1, 3, 224, 224])
    expected_shape = input_details[0]['shape']
    expected_height = expected_shape[2] if expected_shape[1] == 3 else expected_shape[1]
    expected_width = expected_shape[3] if expected_shape[1] == 3 else expected_shape[2]

    # 2. Procesar Imagen
    img = Image.open(img_path).convert('RGB')
    img = img.resize((expected_width, expected_height))
    
    # Normalización estándar (Mean/Std 0.5)
    input_data = np.array(img, dtype=np.float32) / 255.0
    input_data = (input_data - 0.5) / 0.5
    
    # 3. CORRECCIÓN CRÍTICA DE DIMENSIONES
    # Detectar si el modelo pide canales primero (PyTorch style: NCHW) o último (TFLite style: NHWC)
    
    # Caso A: El modelo pide [1, 3, 224, 224] (NCHW) -> Lo usual con ai_edge_torch
    if expected_shape[1] == 3: 
        # La imagen viene como (224, 224, 3), hay que pasarla a (3, 224, 224)
        input_data = np.transpose(input_data, (2, 0, 1))
        
    # Caso B: El modelo pide [1, 224, 224, 3] (NHWC)
    elif expected_shape[3] == 3:
        # No hacemos transpose, la imagen ya está en (224, 224, 3)
        pass
        
    # Agregar dimensión de Batch (1, ...)
    input_data = np.expand_dims(input_data, axis=0)
    
    # 4. Aseguramiento final de forma
    # Si por alguna razón las dimensiones no calzan, forzamos el reshape seguro
    if list(input_data.shape) != list(expected_shape):
        try:
            input_data = input_data.reshape(expected_shape)
        except ValueError:
            print(f"❌ Error Fatal: La imagen {input_data.shape} no cabe en el modelo {expected_shape}")
            return 0 # Retornar valor seguro
            
    # 5. Inferencia
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return np.argmax(output_data)
# --- Segmentación (MediaPipe + TFLite) ---

def get_facemesh_mask(img_path, feature_type):
    """
    Genera máscara para 'lips' o 'skin' usando MediaPipe FaceMesh.
    """
    if not MEDIAPIPE_AVAILABLE:
        return None
    
    mp_face_mesh = mp.solutions.face_mesh
    
    # Índices de landmarks (aproximados para FaceMesh)
    # Labios
    LIPS_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
    # Contorno de cara (para piel)
    FACE_OVAL_INDICES = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

    image = cv2.imread(img_path)
    if image is None: return None
    h, w, _ = image.shape
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5) as face_mesh:
        
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
            
        landmarks = results.multi_face_landmarks[0].landmark
        
        mask = np.zeros((h, w), dtype=np.uint8)
        
        indices = LIPS_INDICES if feature_type == 'lips' else FACE_OVAL_INDICES
        points = []
        for idx in indices:
            pt = landmarks[idx]
            points.append((int(pt.x * w), int(pt.y * h)))
            
        points = np.array(points, dtype=np.int32)
        
        # Dibujar polígono relleno
        cv2.fillPoly(mask, [points], 255)
        
        # Si es piel, restar ojos y boca para ser más precisos (opcional, aquí simplificado)
        if feature_type == 'skin':
            # Restar boca
            lips_points = []
            for idx in LIPS_INDICES:
                pt = landmarks[idx]
                lips_points.append((int(pt.x * w), int(pt.y * h)))
            cv2.fillPoly(mask, [np.array(lips_points, dtype=np.int32)], 0)
            
        # Aplicar máscara
        masked_img = cv2.bitwise_and(image, image, mask=mask)
        return masked_img

def get_hair_mask_mediapipe(img_path, model_path):
    """
    Genera máscara de pelo usando MediaPipe Image Segmenter (API de alto nivel).
    Maneja ops personalizados internamente mejor que tflite puro.
    """
    if not MEDIAPIPE_AVAILABLE:
        return None
    
    try:
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.ImageSegmenterOptions(base_options=base_options,
                                              output_category_mask=True)
        
        with vision.ImageSegmenter.create_from_options(options) as segmenter:
            image = mp.Image.create_from_file(img_path)
            segmentation_result = segmenter.segment(image)
            category_mask = segmentation_result.category_mask
            
            # Convertir a numpy
            mask_np = category_mask.numpy_view()
            
            # El modelo de pelo suele tener clase 1 para pelo
            # A veces es multiclass, pero hair_segmentation.tflite suele ser binario o 2 clases
            binary_mask = (mask_np == 1).astype(np.uint8) * 255
            
            # Redimensionar si es necesario (aunque mp.Image ya maneja esto, la salida es del tamaño de entrada)
            img = cv2.imread(img_path)
            if img.shape[:2] != binary_mask.shape:
                binary_mask = cv2.resize(binary_mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
                
            masked_img = cv2.bitwise_and(img, img, mask=binary_mask)
            return masked_img
            
    except Exception as e:
        print(f"   ⚠️ Error en MediaPipe ImageSegmenter: {e}")
        return None

def get_hair_mask_tflite(img_path, model_path):
    """
    Genera máscara de pelo usando el modelo TFLite de MediaPipe Hair Segmentation.
    """
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # El modelo de pelo suele esperar 512x512 RGBA o RGB float32
    input_shape = input_details[0]['shape'] # [1, 512, 512, 4] usualmente
    h_model, w_model = input_shape[1], input_shape[2]
    
    img = cv2.imread(img_path)
    if img is None: return None
    h_orig, w_orig, _ = img.shape
    
    img_resized = cv2.resize(img, (w_model, h_model))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    
    # Normalización (0-1)
    input_data = img_rgb.astype(np.float32) / 255.0
    
    # Si el modelo espera 4 canales (RGBA), agregar canal alfa
    if input_shape[3] == 4:
        alpha = np.ones((h_model, w_model, 1), dtype=np.float32)
        input_data = np.concatenate((input_data, alpha), axis=-1)
        
    input_data = np.expand_dims(input_data, axis=0)
    
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    # Salida: Máscara de segmentación (usualmente canal 1 de 2, o canal único)
    output_data = interpreter.get_tensor(output_details[0]['index'])
    # output_data shape: [1, 512, 512, 2] (background, hair)
    
    hair_mask = output_data[0, :, :, 1] # Canal de pelo
    
    # Redimensionar máscara al tamaño original
    hair_mask_resized = cv2.resize(hair_mask, (w_orig, h_orig))
    binary_mask = (hair_mask_resized > 0.5).astype(np.uint8) * 255
    
    masked_img = cv2.bitwise_and(img, img, mask=binary_mask)
    return masked_img

def get_facer_mask_tflite(img_path, feature_type, model_path):
    """
    Usa el modelo FaRL (BiSeNet) convertido a TFLite para segmentación precisa.
    Reemplaza a MediaPipe y Haar Cascades.
    """
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Input shape: [1, 3, 448, 448]
    input_shape = input_details[0]['shape']
    h_model, w_model = input_shape[2], input_shape[3]
    
    img = cv2.imread(img_path)
    if img is None: return None
    h_orig, w_orig, _ = img.shape
    
    # 1. Detectar cara para hacer crop
    # Intentar usar MediaPipe Face Detection primero (más preciso que Haar)
    face_crop = None
    x1, y1, x2, y2 = 0, 0, w_orig, h_orig
    
    if MEDIAPIPE_AVAILABLE:
        try:
            mp_face_detection = mp.solutions.face_detection
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
                results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if results.detections:
                    # Tomar la cara con mayor score
                    detection = max(results.detections, key=lambda d: d.score[0])
                    bboxC = detection.location_data.relative_bounding_box
                    
                    x = int(bboxC.xmin * w_orig)
                    y = int(bboxC.ymin * h_orig)
                    w = int(bboxC.width * w_orig)
                    h = int(bboxC.height * h_orig)
                    
                    # Expandir crop para incluir contexto (pelo, cuello)
                    # FaRL funciona mejor con un crop generoso y cuadrado
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Usar la dimensión mayor para hacer un cuadrado
                    size = max(w, h)
                    # Factor de expansión (1.5x para asegurar pelo y barbilla)
                    size = int(size * 1.5)
                    
                    x1 = max(0, center_x - size // 2)
                    y1 = max(0, center_y - size // 2)
                    x2 = min(w_orig, center_x + size // 2)
                    y2 = min(h_orig, center_y + size // 2)
                    
                    face_crop = img[y1:y2, x1:x2]
        except Exception as e:
            print(f"   ⚠️ MediaPipe Detection falló: {e}")

    # Fallback a Haar Cascade si MediaPipe falla o no detecta nada
    if face_crop is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            cascade_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 4)
        
        if len(faces) > 0:
            # Tomar la cara más grande
            x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
            # Expandir un poco el crop para incluir pelo
            margin = int(w * 0.5)
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(w_orig, x + w + margin)
            y2 = min(h_orig, y + h + margin)
            face_crop = img[y1:y2, x1:x2]
        else:
            # Si no detecta cara, usar toda la imagen (fallback)
            face_crop = img
            x1, y1, x2, y2 = 0, 0, w_orig, h_orig

    # 2. Preprocesar
    crop_resized = cv2.resize(face_crop, (w_model, h_model))
    crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
    
    # Normalización 0-1 (FaRL espera float32 0-1)
    input_data = crop_rgb.astype(np.float32) / 255.0
    
    # Transponer a NCHW [1, 3, 448, 448]
    input_data = np.transpose(input_data, (2, 0, 1))
    input_data = np.expand_dims(input_data, axis=0)
    
    # 3. Inferencia
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    # 4. Procesar Salida
    # Output shape: [1, 11, 448, 448] (Logits)
    output_data = interpreter.get_tensor(output_details[0]['index'])
    logits = output_data[0] # [11, 448, 448]
    
    # Argmax para obtener mapa de clases
    mask_map = np.argmax(logits, axis=0).astype(np.uint8) # [448, 448]
    
    # Mapeo de clases LaPa:
    # 0: background, 1: skin, 2: l_brow, 3: r_brow, 4: l_eye, 5: r_eye
    # 6: nose, 7: u_lip, 8: i_mouth, 9: l_lip, 10: hair
    
    final_mask = np.zeros_like(mask_map)
    
    if feature_type == 'skin':
        final_mask[mask_map == 1] = 1
        final_mask[mask_map == 6] = 1 # Incluir nariz
    elif feature_type == 'lips':
        final_mask[mask_map == 7] = 1 # Labio superior
        final_mask[mask_map == 9] = 1 # Labio inferior
    elif feature_type == 'hair':
        final_mask[mask_map == 10] = 1
        final_mask[mask_map == 2] = 1 # Cejas (opcional)
        final_mask[mask_map == 3] = 1
        
    # 5. Post-procesar máscara
    # Redimensionar al tamaño del crop
    mask_resized = cv2.resize(final_mask, (x2-x1, y2-y1), interpolation=cv2.INTER_NEAREST)
    
    # Insertar en máscara completa
    full_mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
    full_mask[y1:y2, x1:x2] = mask_resized
    
    # Aplicar a imagen original
    masked_img = cv2.bitwise_and(img, img, mask=full_mask * 255)
    return masked_img

def get_simple_mask(img_path, feature_type):
    """
    Método de respaldo usando Haar Cascades (OpenCV) si MediaPipe falla.
    """
    # Cargar Haar Cascade para rostro frontal
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if not os.path.exists(cascade_path):
        # Intentar ruta común en sistemas Linux si no está en cv2.data
        cascade_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
        
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("⚠️ No se encontró haarcascade_frontalface_default.xml")
        return None

    img = cv2.imread(img_path)
    if img is None: return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0: return None
    
    # Tomar el rostro más grande
    x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    if feature_type == 'skin':
        # Elipse en el centro de las mejillas (aprox)
        center = (x + w//2, y + h//2)
        axes = (w//4, h//3) 
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        
    elif feature_type == 'lips':
        # Rectángulo en el tercio inferior central
        lx, ly = x + w//3, y + 2*h//3 + h//10
        lw, lh = w//3, h//6
        cv2.rectangle(mask, (lx, ly), (lx+lw, ly+lh), 255, -1)
        
    elif feature_type == 'hair':
        # Aproximación: Arco sobre la frente y costados
        # Centro de la cabeza (arriba de la cara)
        center_x = x + w//2
        center_y = y + h//3
        axes = (int(w*0.6), int(h*0.5))
        
        # Dibujar elipse completa para el pelo
        cv2.ellipse(mask, (center_x, center_y), axes, 0, 0, 360, 255, -1)
        
        # Restar la cara (óvalo central) para dejar solo el "marco" de pelo
        face_axes = (int(w*0.35), int(h*0.45))
        face_center = (x + w//2, y + h//2)
        cv2.ellipse(mask, face_center, face_axes, 0, 0, 360, 0, -1)
        
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img

# --- Lógica Principal ---

def analyze_feature(img_path, feature_name, mask_type, method='mediapipe', verbose=False):
    mask_filename = f"{mask_type}_mask.jpg"
    
    if verbose: print(f"\n🔍 Analizando: {feature_name} (Método: {method})")
    
    # 1. Generar Máscara
    masked_img = None
    
    if method == 'facer_tflite':
        # Nuevo método unificado usando el modelo convertido
        if verbose: print("   🤖 Generando máscara con Facer TFLite (BiSeNet)...")
        try:
            facer_path = get_model_path(FACER_MODEL_NAME)
            masked_img = get_facer_mask_tflite(img_path, mask_type, facer_path)
        except Exception as e:
            return {"feature": feature_name, "error": f"Fallo Facer TFLite: {e}"}

    elif mask_type in ['lips', 'skin']:
        if method == 'mediapipe':
            if verbose: print("   🎭 Generando máscara con MediaPipe FaceMesh...")
            masked_img = get_facemesh_mask(img_path, mask_type)
        else:
            if verbose: print("   🗿 Generando máscara con Haar Cascade (Simple)...")
            masked_img = get_simple_mask(img_path, mask_type)
        
    elif mask_type == 'hair':
        if method == 'simple':
             if verbose: print("   💇 Generando máscara con Haar Cascade (Simple)...")
             masked_img = get_simple_mask(img_path, mask_type)
        else:
            if verbose: print("   💇 Generando máscara con MediaPipe Image Segmenter...")
            try:
                hair_model_path = get_model_path(HAIR_MODEL_NAME, HAIR_MODEL_URL)
                # Intentar primero con la API de MediaPipe (más robusta para este modelo)
                masked_img = get_hair_mask_mediapipe(img_path, hair_model_path)
                
                if masked_img is None:
                    if verbose: print("   ⚠️ MediaPipe falló, intentando TFLite puro...")
                    masked_img = get_hair_mask_tflite(img_path, hair_model_path)
                    
            except Exception as e:
                print(f"   ⚠️ Fallo modelo pelo ({e}). Usando método simple...")
                masked_img = None
            
            if masked_img is None:
                 if verbose: print("   ⚠️ Fallaron modelos ML. Usando método simple...")
                 masked_img = get_simple_mask(img_path, mask_type)
            
    if masked_img is None:
        return {"feature": feature_name, "error": "No se pudo generar la máscara"}
        
    cv2.imwrite(mask_filename, masked_img)
    if verbose: print(f"   ✅ Máscara guardada: {mask_filename}")
    
    # 2. Clasificar Color
    try:
        resnet_path = get_model_path(RESNET_MODEL_NAME)
        if verbose: print("   🧠 Inferencia de color (TFLite)...")
        
        raw_ans = predict_season_tflite(mask_filename, resnet_path)
        ans = map_model_output(raw_ans)
        
        return {
            "feature": feature_name,
            "season_name": SEASON_NAMES.get(ans, "Desconocido"),
            "description": SEASON_DESCRIPTIONS.get(ans, ""),
            "mask_file": mask_filename
        }
    except Exception as e:
        return {"feature": feature_name, "error": f"Fallo inferencia: {e}"}

def main():
    parser = argparse.ArgumentParser(description="ColorInsight - TFLite Only")
    parser.add_argument('-r', '--ruta', type=str, required=True, help='Imagen a analizar')
    parser.add_argument('-v', '--verbose', action='store_true', help='Ver detalles')
    parser.add_argument('-m', '--method', type=str, default='simple', choices=['mediapipe', 'simple', 'facer_tflite'], 
                        help='Método de segmentación: "mediapipe" (requiere MediaPipe), "simple" (Haar - por defecto), "facer_tflite" (Modelo convertido)')
    args = parser.parse_args()
    
    if not os.path.exists(args.ruta):
        print(f"❌ Archivo no encontrado: {args.ruta}")
        sys.exit(1)
    
    if args.method == 'mediapipe' and not MEDIAPIPE_AVAILABLE:
        print("❌ Error: El método 'mediapipe' requiere MediaPipe instalado.")
        print("   Opciones: 1) pip install mediapipe")
        print("            2) Usa --method simple (no requiere MediaPipe)")
        sys.exit(1)
        
    tasks = [("Piel", "skin"), ("Pelo", "hair"), ("Labios", "lips")]
    results = {}
    
    print("\n" + "🌟"*40)
    print(f"   COLORINSIGHT - TFLITE ONLY ({args.method.upper()})")
    print("🌟"*40)
    
    iterator = tasks if args.verbose else tqdm(tasks, desc="Procesando")
    
    for name, mtype in iterator:
        results[name] = analyze_feature(args.ruta, name, mtype, args.method, args.verbose)
        
    print("\n" + "="*60)
    print("📋 RESUMEN FINAL")
    print("="*60)
    
    for name, res in results.items():
        if "error" in res:
            print(f"❌ {name}: {res['error']}")
        else:
            print(f"✅ {name}: {res['season_name']}")
            
    print("\n✨ Listo.")

if __name__ == "__main__":
    main()
