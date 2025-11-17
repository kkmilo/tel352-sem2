#!/usr/bin/env python3
"""Entrenamiento de un modelo DNN para estimar estatura.

Uso:
    python scripts/entrenar_dnn_altura.py --dataset data/altura_features.csv \
        --epochs 120 --hidden 128 64 --salida modelos/

El dataset esperado debe contener columnas:
    height_cm (variable objetivo)
    y exactamente las 15 columnas de características usadas por la app, por ejemplo:
        leg_to_torso_ratio, height_to_width_ratio, image_width, confidence_avg, ... etc.

Genera:
    modelos/modelo_altura_dnn_<timestamp>.tflite
    modelos/modelo_metadata_<timestamp>.json
    modelos/scaler_<timestamp>.pkl
    modelos/calibracion_<timestamp>.json (opcional si se pasa --calibration-file)

Notas:
 - Este script es un punto de partida; ajusta arquitectura y regularización según tus datos reales.
 - Para cuantización post-entrenamiento cambia el flag --quantize.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

try:
    import tensorflow as tf
except Exception as e:  # pragma: no cover
    raise SystemExit("TensorFlow no está instalado. Instala tensorflow>=2.12.0 para usar este script.") from e


def build_model(input_dim: int, hidden_layers: list[int], lr: float = 1e-3) -> tf.keras.Model:
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(input_dim,)))
    for h in hidden_layers:
        model.add(tf.keras.layers.Dense(h, activation='relu'))
        model.add(tf.keras.layers.Dropout(0.1))
    model.add(tf.keras.layers.Dense(1, activation='linear'))
    model.compile(optimizer=tf.keras.optimizers.Adam(lr), loss='mae', metrics=['mae'])
    return model


def convert_to_tflite(model: tf.keras.Model, output_path: Path, quantize: bool = False):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    output_path.write_bytes(tflite_model)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True, help='Ruta al CSV con features + height_cm')
    parser.add_argument('--target', default='height_cm', help='Nombre de la columna objetivo')
    parser.add_argument('--hidden', nargs='+', type=int, default=[128, 64], help='Capas ocultas')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--val-split', type=float, default=0.15)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--quantize', action='store_true', help='Aplicar cuantización post-entrenamiento')
    parser.add_argument('--salida', default='modelos', help='Directorio de salida de artefactos')
    parser.add_argument('--calibration-file', help='JSON con offset de calibración (ej: {"offset_aditivo": 8.78})')
    args = parser.parse_args()

    salida_dir = Path(args.salida)
    salida_dir.mkdir(exist_ok=True, parents=True)

    df = pd.read_csv(args.dataset)
    if args.target not in df.columns:
        raise ValueError(f"Columna objetivo '{args.target}' no encontrada en el dataset")

    y = df[args.target].astype(float).to_numpy()
    x_df = df.drop(columns=[args.target])
    feature_names = list(x_df.columns)
    X = x_df.to_numpy(dtype=np.float32)

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=args.val_split, random_state=42)

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = build_model(x_train_scaled.shape[1], args.hidden, lr=args.lr)

    early = tf.keras.callbacks.EarlyStopping(patience=12, restore_best_weights=True)
    model.fit(
        x_train_scaled, y_train,
        validation_data=(x_test_scaled, y_test),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=[early],
        verbose=1
    )

    # Evaluación
    pred_test = model.predict(x_test_scaled).reshape(-1)
    mae = mean_absolute_error(y_test, pred_test)
    r2 = r2_score(y_test, pred_test)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    tflite_path = salida_dir / f'modelo_altura_dnn_{timestamp}.tflite'
    convert_to_tflite(model, tflite_path, quantize=args.quantize)

    scaler_path = salida_dir / f'scaler_{timestamp}.pkl'
    joblib.dump(scaler, scaler_path)

    metadata = {
        'timestamp': timestamp,
        'model_type': 'DNNRegressor',
        'model_name': f'modelo_altura_dnn_{timestamp}',
        'dataset': 'ANSUR II (Datos Reales / Derivado)',
        'features': len(feature_names),
        'feature_names': feature_names,
        'hidden_layers': args.hidden,
        'train_params': {
            'epochs': args.epochs,
            'batch_size': args.batch_size,
            'learning_rate': args.lr,
            'quantized': args.quantize
        },
        'test_metrics': {
            'mae': float(mae),
            'r2': float(r2)
        }
    }

    metadata_path = salida_dir / f'modelo_metadata_{timestamp}.json'
    metadata_path.write_text(json.dumps(metadata, indent=2))

    if args.calibration_file:
        calib_src = Path(args.calibration_file)
        if calib_src.exists():
            calib_target = salida_dir / f'calibracion_{timestamp}.json'
            calib_target.write_bytes(calib_src.read_bytes())

    print("\n  Entrenamiento y conversión completados")
    print(f"   MAE test: {mae:.2f} cm  R2: {r2:.3f}")
    print(f"   Modelo TFLite: {tflite_path}")
    print(f"   Scaler: {scaler_path}")
    print(f"   Metadata: {metadata_path}")


if __name__ == '__main__':
    main()
