#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Procesar múltiples imágenes con ColorInsight
"""

import os
import sys
import json
from pathlib import Path

# Importar el módulo principal
import colorInsight


def procesar_directorio(ruta_directorio, output_file="resultados.json"):
    """
    Procesa todas las imágenes en un directorio
    
    Args:
        ruta_directorio: Ruta al directorio con imágenes
        output_file: Archivo donde guardar los resultados
    """
    extensiones_validas = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    
    directorio = Path(ruta_directorio)
    
    if not directorio.exists():
        print(f"❌ El directorio no existe: {ruta_directorio}")
        return
    
    # Encontrar todas las imágenes
    imagenes = []
    for ext in extensiones_validas:
        imagenes.extend(directorio.glob(f"*{ext}"))
        imagenes.extend(directorio.glob(f"*{ext.upper()}"))
    
    if not imagenes:
        print(f"❌ No se encontraron imágenes en: {ruta_directorio}")
        return
    
    print(f"\n📁 Encontradas {len(imagenes)} imágenes")
    print("🚀 Iniciando procesamiento por lotes...\n")
    
    resultados = {}
    
    for i, imagen in enumerate(imagenes, 1):
        print(f"\n{'='*60}")
        print(f"Procesando {i}/{len(imagenes)}: {imagen.name}")
        print('='*60)
        
        try:
            resultado = colorInsight.analizar_completo(str(imagen))
            resultados[imagen.name] = resultado
        except Exception as e:
            print(f"❌ Error procesando {imagen.name}: {e}")
            resultados[imagen.name] = {"error": str(e)}
    
    # Guardar resultados
    output_path = directorio / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Resultados guardados en: {output_path}")
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DEL PROCESAMIENTO")
    print("="*60)
    
    exitosos = sum(1 for r in resultados.values() if "error" not in r.get("tono_piel", {}))
    print(f"Total de imágenes: {len(imagenes)}")
    print(f"Procesadas exitosamente: {exitosos}")
    print(f"Con errores: {len(imagenes) - exitosos}")
    
    # Distribución de temporadas
    temporadas_piel = {}
    temporadas_labios = {}
    
    for nombre, resultado in resultados.items():
        if "error" not in resultado.get("tono_piel", {}):
            temporada = resultado["tono_piel"].get("temporada", "Desconocido")
            temporadas_piel[temporada] = temporadas_piel.get(temporada, 0) + 1
        
        if "error" not in resultado.get("color_labios", {}):
            temporada = resultado["color_labios"].get("temporada", "Desconocido")
            temporadas_labios[temporada] = temporadas_labios.get(temporada, 0) + 1
    
    if temporadas_piel:
        print("\n🎨 Distribución de Tonos de Piel:")
        for temporada, count in sorted(temporadas_piel.items(), key=lambda x: x[1], reverse=True):
            print(f"   {temporada}: {count} ({count/exitosos*100:.1f}%)")
    
    if temporadas_labios:
        print("\n💄 Distribución de Color de Labios:")
        for temporada, count in sorted(temporadas_labios.items(), key=lambda x: x[1], reverse=True):
            print(f"   {temporada}: {count} ({count/exitosos*100:.1f}%)")
    
    print("\n" + "="*60 + "\n")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python procesar_lote.py <directorio_con_imagenes>")
        print("Ejemplo: python procesar_lote.py C:/Users/fotos/")
        sys.exit(1)
    
    ruta_directorio = sys.argv[1]
    procesar_directorio(ruta_directorio)


if __name__ == "__main__":
    main()
