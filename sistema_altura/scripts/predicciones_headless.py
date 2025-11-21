#!/usr/bin/env python3
"""
Script headless para generar predicciones sin GUI, desde cámara o imágenes.

- Carga automáticamente el último modelo TFLite en modelos/
- Carga scaler, metadata y calibración (si existe)
- Modo cámara: abre la cámara, obtiene pose, extrae 15 features en el mismo
    orden del entrenamiento, ejecuta TFLite y guarda resultados (imagen anotada + JSON)
- Modo imágenes: procesa una carpeta de imágenes (--images-dir) o una sola imagen (--image)

Uso:
    # Desde cámara
    python scripts/predicciones_headless.py --num 5 --device 0 --cooldown 1.5

    # Procesar una carpeta de imágenes (hasta N)
    python scripts/predicciones_headless.py --images-dir capturas_estatura --num 10

    # Procesar una sola imagen
    python scripts/predicciones_headless.py --image capturas_estatura/mi_foto.jpg

Requisitos: opencv-python, mediapipe, numpy, joblib, tflite-runtime (o tensorflow>=2.19 como fallback)
"""
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
try:
    import mediapipe as mp
except ModuleNotFoundError:
    import sys
    print("❌ Error: mediapipe no está instalado en este entorno.")
    print("   Posibles causas:")
    print("     • Ejecutaste el script con el Python del sistema en lugar del entorno virtual.")
    print("     • No corriste ./scripts/instalar_dependencias.sh después de crear el venv.")
    print("\n   Solución rápida:")
    print("     1) source venv/bin/activate")
    print("     2) ./scripts/instalar_dependencias.sh")
    print("     3) ./scripts/predicciones_headless.py --num 5")
    print("\n   Si ya estás en el venv y falla, verifica que 'mediapipe' esté en requirements.txt.")
    sys.exit(1)
import joblib

# Intérprete TFLite (tflite-runtime o tensorflow)
try:
    from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter  # type: ignore
except Exception:
    import tensorflow as tf  # type: ignore
    TFLiteInterpreter = tf.lite.Interpreter  # type: ignore[attr-defined]

MODEL_PATTERN_TFLITE = 'modelo_altura_*.tflite'


def cargar_modelo_automatico():
    """Localiza y carga el modelo TFLite más reciente con su scaler, metadata y calibración."""
    project_root = Path(__file__).resolve().parents[1]
    modelos_dir = project_root / 'modelos'
    modelos = list(modelos_dir.glob(MODEL_PATTERN_TFLITE))
    if not modelos:
        raise FileNotFoundError(f"No se encontraron modelos TFLite en {modelos_dir}")

    modelo_path = max(modelos, key=lambda p: p.stat().st_mtime)
    parts = modelo_path.stem.split('_')
    timestamp = '_'.join(parts[-2:])

    # Cargar TFLite
    interpreter = TFLiteInterpreter(model_path=str(modelo_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Cargar scaler
    scaler_path = modelo_path.parent / f'scaler_{timestamp}.pkl'
    if not scaler_path.exists():
        scaler_path = modelo_path.parent / f'scaler_altura_{timestamp}.pkl'
    scaler = joblib.load(scaler_path)

    # Metadata
    metadata_path = modelo_path.parent / f'modelo_metadata_{timestamp}.json'
    if not metadata_path.exists():
        metadata_path = modelo_path.parent / f'modelo_altura_{timestamp}.json'
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Calibración (opcional)
    calibracion = None
    calibracion_path = modelo_path.parent / f'calibracion_{timestamp}.json'
    if calibracion_path.exists():
        with open(calibracion_path, 'r') as f:
            calibracion = json.load(f)

    return {
        'root': project_root,
        'modelo_dir': modelos_dir,
        'timestamp': timestamp,
        'interpreter': interpreter,
        'input_details': input_details,
        'output_details': output_details,
        'scaler': scaler,
        'metadata': metadata,
        'calibracion': calibracion,
    }


def extraer_caracteristicas(image, landmarks):
    """Extrae 15 características (mismo orden que el entrenamiento)."""
    h, w = image.shape[:2]
    lm = landmarks.landmark

    nose = lm[0]
    left_shoulder = lm[11]
    right_shoulder = lm[12]
    left_hip = lm[23]
    right_hip = lm[24]
    left_ankle = lm[27]
    right_ankle = lm[28]

    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_mid_y = (left_hip.y + right_hip.y) / 2
    ankle_mid_y = (left_ankle.y + right_ankle.y) / 2

    body_height_px = (ankle_mid_y - nose.y) * h
    leg_length_px = (ankle_mid_y - hip_mid_y) * h
    torso_length_px = (hip_mid_y - shoulder_mid_y) * h
    shoulder_width_px = abs(right_shoulder.x - left_shoulder.x) * w
    hip_width_px = abs(right_hip.x - left_hip.x) * w

    leg_to_torso_ratio = leg_length_px / (torso_length_px + 1e-6)
    height_to_width_ratio = body_height_px / (shoulder_width_px + 1e-6)

    nose_visibility = nose.visibility
    left_shoulder_visibility = left_shoulder.visibility
    right_shoulder_visibility = right_shoulder.visibility
    left_hip_visibility = left_hip.visibility
    right_hip_visibility = right_hip.visibility
    confidence_avg = np.mean([
        lm[i].visibility for i in [0, 11, 12, 23, 24, 25, 26, 27, 28]
    ])

    image_width = w
    image_height = h

    return [
        body_height_px,
        leg_length_px,
        torso_length_px,
        shoulder_width_px,
        hip_width_px,
        leg_to_torso_ratio,
        height_to_width_ratio,
        image_width,
        image_height,
        confidence_avg,
        nose_visibility,
        left_shoulder_visibility,
        right_shoulder_visibility,
        left_hip_visibility,
        right_hip_visibility,
    ]


def calcular_confianza(caracteristicas, visibility):
    conf = visibility * 0.6
    leg_torso_ratio = caracteristicas[5]
    conf += 0.2 if 0.8 < leg_torso_ratio < 1.5 else 0.1
    body_height_px = caracteristicas[0]
    conf += 0.2 if 300 < body_height_px < 1200 else 0.1
    return min(conf, 0.99)


def crear_imagen_anotada(image, landmarks, altura_pred, confianza):
    img = image.copy()
    h, w = img.shape[:2]

    # puntos
    for l in landmarks.landmark:
        if l.visibility > 0.5:
            x, y = int(l.x * w), int(l.y * h)
            cv2.circle(img, (x, y), 4, (0, 255, 0), -1)

    # conexiones básicas
    conexiones = [(11, 12), (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28)]
    for a, b in conexiones:
        la, lb = landmarks.landmark[a], landmarks.landmark[b]
        if la.visibility > 0.5 and lb.visibility > 0.5:
            x1, y1 = int(la.x * w), int(la.y * h)
            x2, y2 = int(lb.x * w), int(lb.y * h)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

    # caja info
    cv2.rectangle(img, (10, 10), (w - 10, 150), (0, 0, 0), -1)
    cv2.rectangle(img, (10, 10), (w - 10, 150), (0, 255, 0), 3)
    cv2.putText(img, f"ALTURA PREDICHA: {altura_pred:.1f} cm", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(img, f"Confianza: {confianza:.1%}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=5, help='Número de predicciones a realizar')
    parser.add_argument('--device', type=int, default=0, help='Índice de cámara (0 por defecto)')
    parser.add_argument('--cooldown', type=float, default=1.5, help='Segundos entre predicciones (modo cámara)')
    parser.add_argument('--images-dir', type=str, default='', help='Procesa imágenes existentes en esta carpeta en lugar de usar la cámara')
    parser.add_argument('--image', type=str, default='', help='Ruta a una sola imagen para procesar en lugar de usar la cámara')
    args = parser.parse_args()

    cfg = cargar_modelo_automatico()
    print(f"✅ Modelo cargado | Timestamp: {cfg['timestamp']} | Dir: {cfg['modelo_dir']}")

    resultados_dir = cfg['root'] / 'resultados_predicciones'
    capturas_dir = cfg['root'] / 'capturas_estatura'
    resultados_dir.mkdir(exist_ok=True)
    capturas_dir.mkdir(exist_ok=True)

    mp_pose = mp.solutions.pose
    # En modo imágenes, usar static_image_mode=True para procesar frame a frame más rápido/robusto
    static_mode = bool(args.images_dir)
    pose = mp_pose.Pose(static_image_mode=static_mode, model_complexity=2, enable_segmentation=False,
                        min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Modo imágenes si se especifica --images-dir o --image
    usar_imagenes = bool(args.images_dir or args.image)
    cap = None
    image_files = []
    if usar_imagenes:
        if args.image:
            img_path = Path(args.image).expanduser().resolve()
            if not img_path.exists():
                raise FileNotFoundError(f"No existe la imagen: {img_path}")
            if img_path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
                raise ValueError(f"Extensión no soportada: {img_path.suffix} (use .jpg/.jpeg/.png)")
            image_files = [img_path]
            args.num = 1  # Forzar 1 predicción para imagen única
            print(f"🖼️  Procesando 1 imagen: {img_path}")
        else:
            base = Path(args.images_dir).expanduser().resolve()
            if not base.exists():
                raise FileNotFoundError(f"No existe la carpeta de imágenes: {base}")
            all_imgs = sorted([p for p in base.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
            if not all_imgs:
                raise FileNotFoundError(f"No se encontraron imágenes en {base}")
            image_files = all_imgs[: max(1, args.num)]
            print(f"🖼️  Procesando {len(image_files)} imágenes desde {base}")
    else:
        cap = cv2.VideoCapture(args.device)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara. Verifica permisos y /dev/video*")

    buenas = 0
    intentos = 0
    max_intentos = args.num * 8  # tolerancia si no detecta pose

    alturas = []

    while buenas < args.num and (usar_imagenes or intentos < max_intentos):
        intentos += 1
        if usar_imagenes:
            if buenas >= len(image_files):
                break
            frame = cv2.imread(str(image_files[buenas]))
            if frame is None:
                continue
        else:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        if not res.pose_landmarks:
            time.sleep(0.1)
            continue

        # Extraer características y visibilidad
        feats = extraer_caracteristicas(frame, res.pose_landmarks)
        visibility = feats[9]
        X = np.array(feats, dtype=np.float32).reshape(1, -1)
        x_scaled = cfg['scaler'].transform(X)

        # Inferencia TFLite
        inp_idx = cfg['input_details'][0]['index']
        out_idx = cfg['output_details'][0]['index']
        inp = x_scaled.astype(cfg['input_details'][0]['dtype'])
        cfg['interpreter'].set_tensor(inp_idx, inp)
        cfg['interpreter'].invoke()
        out = cfg['interpreter'].get_tensor(out_idx)
        altura_raw = float(out.reshape(-1)[0])
        altura_cal = altura_raw

        if cfg['calibracion']:
            altura_cal -= float(52.0)

        conf = calcular_confianza(feats, visibility)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        if usar_imagenes:
            cap_name = image_files[buenas]
        else:
            cap_name = capturas_dir / f"captura_headless_{ts}.jpg"
            cv2.imwrite(str(cap_name), frame)

        anotada = crear_imagen_anotada(frame, res.pose_landmarks, altura_cal, conf)
        out_img = resultados_dir / f"prediccion_headless_{ts}.jpg"
        cv2.imwrite(str(out_img), anotada)

        resultado = {
            'timestamp': ts,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'imagen_original': str(cap_name),
            'imagen_anotada': str(out_img),
            'altura_predicha_cm': round(altura_cal, 2),
            'altura_sin_calibracion_cm': round(altura_raw, 2),
            'confianza': round(conf, 4),
            'visibilidad_landmarks': round(visibility, 4),
            'caracteristicas': {
                'body_height_px': round(feats[0], 2),
                'leg_length_px': round(feats[1], 2),
                'torso_length_px': round(feats[2], 2),
                'shoulder_width_px': round(feats[3], 2),
                'hip_width_px': round(feats[4], 2),
            },
            'modelo_usado': cfg['metadata'].get('model_name', 'N/A'),
            'mae_modelo': round(cfg['metadata'].get('test_metrics', {}).get('mae', 0), 2)
        }
        json_path = resultados_dir / f"prediccion_headless_{ts}.json"
        with open(json_path, 'w') as f:
            json.dump(resultado, f, indent=2)

        alturas.append(resultado)
        buenas += 1
        print(f"[{buenas}/{args.num}] Altura(cal): {resultado['altura_predicha_cm']} cm | Raw: {resultado['altura_sin_calibracion_cm']} cm | Conf: {resultado['confianza']}")
        if not usar_imagenes:
            time.sleep(args.cooldown)

    if cap is not None:
        cap.release()
    pose.close()

    if buenas == 0:
        raise RuntimeError("No se pudieron generar predicciones. Revisa iluminación y encuadre.")

    # Resumen
    raws = [r['altura_sin_calibracion_cm'] for r in alturas]
    cals = [r['altura_predicha_cm'] for r in alturas]
    print("\nResumen de alturas (cm):")
    print("  Raw:", raws)
    print("  Cal:", cals)
    if len(cals) > 1:
        print(f"  Cal (promedio): {np.mean(cals):.2f} | Desv.std: {np.std(cals):.2f}")


if __name__ == '__main__':
    # Mensaje adicional si se está ejecutando fuera de venv
    import sys
    venv = os.environ.get('VIRTUAL_ENV')
    if venv is None:
        print("⚠️ Aviso: Parece que no estás dentro de un entorno virtual (VIRTUAL_ENV no definido).")
        print("   Se recomienda: source venv/bin/activate")
    main()
