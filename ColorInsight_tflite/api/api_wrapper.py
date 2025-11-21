import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from .scripts.predicciones_headless import (
    cargar_modelo_automatico,
    extraer_caracteristicas,
    calcular_confianza,
    crear_imagen_anotada,
)
import mediapipe as mp


def run_height_prediction_from_image(pil_image):
    """
    Receives a PIL image and returns:
      - predicted height (cm)
      - raw height
      - confidence
      - annotated image (as numpy array)
    """

    # Convert PIL → OpenCV
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Load model/scaler/metadata
    cfg = cargar_modelo_automatico()

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)

    if not res.pose_landmarks:
        raise ValueError("No pose landmarks detected. Try another image.")

    feats = extraer_caracteristicas(frame, res.pose_landmarks)
    visibility = feats[9]

    X = np.array(feats, dtype=np.float32).reshape(1, -1)
    x_scaled = cfg["scaler"].transform(X)

    # TFLite inference
    inp_idx = cfg["input_details"][0]["index"]
    out_idx = cfg["output_details"][0]["index"]

    cfg["interpreter"].set_tensor(inp_idx, x_scaled.astype(cfg["input_details"][0]["dtype"]))
    cfg["interpreter"].invoke()
    out = cfg["interpreter"].get_tensor(out_idx)

    altura_raw = float(out.reshape(-1)[0])
    altura_cal = altura_raw

    if cfg["calibracion"]:
        altura_cal += float(cfg["calibracion"].get("offset_aditivo", 0.0))

    confianza = calcular_confianza(feats, visibility)

    # Annotated image
    anotada = crear_imagen_anotada(frame, res.pose_landmarks, altura_cal, confianza)

    return {
        "altura_predicha_cm": round(altura_cal, 2),
        "altura_sin_calibracion_cm": round(altura_raw, 2),
        "confianza": round(confianza, 4),
        "annotated_image": anotada,  # numpy array
    }
