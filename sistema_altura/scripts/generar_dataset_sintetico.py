#!/usr/bin/env python3
"""
Genera un dataset sintético de ~4000 muestras con 15 características
simulando distribuciones realistas para entrenamiento del modelo TFLite.

Este script replica la estructura del dataset ANSUR II usado originalmente.
"""
import numpy as np
import pandas as pd
from pathlib import Path

# Semilla para reproducibilidad
np.random.seed(42)

# Número de muestras (similar al original)
N_SAMPLES = 4000

# Distribución de alturas realistas (en cm)
# Media ~170cm, std ~10cm para población mixta
alturas = np.random.normal(loc=170, scale=10, size=N_SAMPLES)
alturas = np.clip(alturas, 150, 200)  # Limitar a rango realista

# Generar características correlacionadas con la altura
# Basado en las importancias del Random Forest original

# 1. leg_to_torso_ratio (importancia: 0.397)
# Mayor correlación con altura
leg_to_torso_ratio = 1.0 + (alturas - 170) * 0.005 + np.random.normal(0, 0.1, N_SAMPLES)
leg_to_torso_ratio = np.clip(leg_to_torso_ratio, 0.8, 1.3)

# 2. height_to_width_ratio (importancia: 0.172)
height_to_width_ratio = 2.5 + (alturas - 170) * 0.01 + np.random.normal(0, 0.2, N_SAMPLES)
height_to_width_ratio = np.clip(height_to_width_ratio, 2.0, 3.5)

# 3. body_height_px (correlacionado con altura real)
body_height_px = alturas * 3.5 + np.random.normal(0, 50, N_SAMPLES)
body_height_px = np.clip(body_height_px, 400, 800)

# 4. leg_length_px
leg_length_px = body_height_px * 0.55 + np.random.normal(0, 30, N_SAMPLES)

# 5. torso_length_px
torso_length_px = body_height_px * 0.45 + np.random.normal(0, 25, N_SAMPLES)

# 6. shoulder_width_px
shoulder_width_px = 80 + (alturas - 170) * 0.3 + np.random.normal(0, 10, N_SAMPLES)
shoulder_width_px = np.clip(shoulder_width_px, 60, 120)

# 7. hip_width_px
hip_width_px = 70 + (alturas - 170) * 0.25 + np.random.normal(0, 8, N_SAMPLES)
hip_width_px = np.clip(hip_width_px, 50, 100)

# 8. image_width (importancia: 0.047)
image_width = np.random.normal(loc=640, scale=50, size=N_SAMPLES)
image_width = np.clip(image_width, 480, 800)

# 9. image_height
image_height = np.random.normal(loc=480, scale=40, size=N_SAMPLES)
image_height = np.clip(image_height, 360, 600)

# 10. confidence_avg (importancia: 0.046)
# Alta confianza en detección
confidence_avg = np.random.beta(8, 2, N_SAMPLES)  # Sesgado hacia valores altos
confidence_avg = np.clip(confidence_avg, 0.5, 1.0)

# 11-15. Visibilidades de puntos clave (nose, left_shoulder, right_shoulder, left_hip, right_hip)
nose_visibility = np.random.beta(9, 1, N_SAMPLES)
left_shoulder_vis = np.random.beta(8, 2, N_SAMPLES)
right_shoulder_vis = np.random.beta(8, 2, N_SAMPLES)
left_hip_vis = np.random.beta(7, 2, N_SAMPLES)
right_hip_vis = np.random.beta(7, 2, N_SAMPLES)

# Crear DataFrame
df = pd.DataFrame({
    'body_height_px': body_height_px,
    'leg_length_px': leg_length_px,
    'torso_length_px': torso_length_px,
    'shoulder_width_px': shoulder_width_px,
    'hip_width_px': hip_width_px,
    'leg_to_torso_ratio': leg_to_torso_ratio,
    'height_to_width_ratio': height_to_width_ratio,
    'image_width': image_width,
    'image_height': image_height,
    'confidence_avg': confidence_avg,
    'nose_visibility': nose_visibility,
    'left_shoulder_visibility': left_shoulder_vis,
    'right_shoulder_visibility': right_shoulder_vis,
    'left_hip_visibility': left_hip_vis,
    'right_hip_visibility': right_hip_vis,
    'height_cm': alturas  # Variable objetivo
})

# Guardar dataset
output_dir = Path(__file__).parent.parent / 'data'
output_dir.mkdir(exist_ok=True, parents=True)
output_path = output_dir / 'altura_features_sintetico.csv'

df.to_csv(output_path, index=False)

print(f"   Dataset sintético generado: {output_path}")
print(f"   Muestras: {len(df)}")
print(f"   Features: {len(df.columns) - 1}")
print(f"\n Estadísticas de altura:")
print(f"   Media: {df['height_cm'].mean():.2f} cm")
print(f"   Std: {df['height_cm'].std():.2f} cm")
print(f"   Min: {df['height_cm'].min():.2f} cm")
print(f"   Max: {df['height_cm'].max():.2f} cm")
