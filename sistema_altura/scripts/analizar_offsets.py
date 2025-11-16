#!/usr/bin/env python3
"""Análisis de offsets de calibración en predicciones headless."""
import json
from pathlib import Path
import numpy as np

res_dir = Path(__file__).parent.parent / "resultados_predicciones"
jsons = sorted(res_dir.glob("prediccion_headless_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

if not jsons:
    print("No se encontraron JSON headless")
    exit(1)

print(f"📊 Análisis de {len(jsons)} predicciones headless:\n")
print(f"{'Timestamp':<20} {'Raw (cm)':<12} {'Calibrada (cm)':<15} {'Offset (cm)':<12} {'Confianza'}")
print("-" * 80)

offsets = []
raws = []
cals = []
confs = []

for js in jsons:
    with open(js) as f:
        data = json.load(f)
    raw = data.get("altura_sin_calibracion_cm", 0)
    cal = data.get("altura_predicha_cm", 0)
    offset = cal - raw
    conf = data.get("confianza", 0)
    ts = data.get("timestamp", "N/A")
    
    offsets.append(offset)
    raws.append(raw)
    cals.append(cal)
    confs.append(conf)
    
    print(f"{ts:<20} {raw:>10.2f}   {cal:>13.2f}   {offset:>10.2f}   {conf:>8.2%}")

print("=" * 80)
print(f"\n📈 Estadísticas:\n")
print(f"  Altura RAW (sin calibración):")
print(f"    Media:  {np.mean(raws):.2f} cm")
print(f"    Desv:   {np.std(raws):.2f} cm")
print(f"    Rango:  [{np.min(raws):.2f}, {np.max(raws):.2f}] cm\n")

print(f"  Altura CALIBRADA (con offset):")
print(f"    Media:  {np.mean(cals):.2f} cm")
print(f"    Desv:   {np.std(cals):.2f} cm")
print(f"    Rango:  [{np.min(cals):.2f}, {np.max(cals):.2f}] cm\n")

print(f"  Offset aplicado (Cal - Raw):")
print(f"    Media:  {np.mean(offsets):.2f} cm")
print(f"    Desv:   {np.std(offsets):.2f} cm")
print(f"    Rango:  [{np.min(offsets):.2f}, {np.max(offsets):.2f}] cm\n")

print(f"  Confianza promedio: {np.mean(confs):.2%}\n")
