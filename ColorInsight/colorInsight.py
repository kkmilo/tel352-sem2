#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ColorInsight - Análisis de Color Personal (Versión Local)
Uso: python colorInsight.py <ruta_imagen>
Ejemplo: python colorInsight.py "C:/Users/foto.jpg"
"""

import sys
import os
from collections import Counter
import argparse

# Importar módulos del proyecto
import functions as f
import skin_model as m


def analizar_tono_piel(ruta_imagen):
    """
    Analiza el tono de piel de una imagen y determina el tipo de color personal
    
    Args:
        ruta_imagen: Ruta al archivo de imagen
        
    Returns:
        dict con el resultado del análisis
    """
    print("\n" + "="*60)
    print("🎨 ANÁLISIS DE TONO DE PIEL (PERSONAL COLOR)")
    print("="*60)
    
    try:
        if not os.path.exists(ruta_imagen):
            return {"error": f"Archivo no encontrado: {ruta_imagen}"}
        
        print(f"📁 Procesando: {ruta_imagen}")
        print("⏳ Extrayendo máscara de piel...")
        
        # Crear archivos temporales
        temp_saved = "temp_saved.jpg"
        temp_mask = "temp_mask.jpg"
        
        # Copiar imagen a archivo temporal
        import shutil
        shutil.copy(ruta_imagen, temp_saved)
        
        # Extraer máscara de piel
        f.save_skin_mask(temp_saved)
        
        print("🧠 Analizando con modelo de deep learning...")
        
        # Analizar con el modelo
        ans = m.get_season("temp.jpg")
        
        # Limpiar archivos temporales
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")
        if os.path.exists(temp_saved):
            os.remove(temp_saved)
        
        # Mapear resultado
        if ans == 3:
            ans = 4
        elif ans == 0:
            ans = 3
        
        # Nombres de temporadas
        season_names = {
            1: "Spring (Primavera)",
            2: "Summer (Verano)", 
            3: "Autumn (Otoño)",
            4: "Winter (Invierno)"
        }
        
        season_descriptions = {
            1: "Tonos cálidos y brillantes - Colores claros y vivos como coral, melocotón, dorado",
            2: "Tonos fríos y suaves - Colores pastel y apagados como lavanda, rosa pálido, azul suave",
            3: "Tonos cálidos y profundos - Colores tierra y ricos como terracota, verde oliva, camel",
            4: "Tonos fríos e intensos - Colores brillantes y contrastantes como negro, blanco puro, rojo intenso"
        }
        
        resultado = {
            "codigo": ans,
            "temporada": season_names.get(ans, "Desconocido"),
            "descripcion": season_descriptions.get(ans, "")
        }
        
        print("\n✅ RESULTADO:")
        print(f"   🎯 Temporada: {resultado['temporada']}")
        print(f"   📊 Código: {resultado['codigo']}")
        print(f"   💡 Descripción: {resultado['descripcion']}")
        
        return resultado
        
    except Exception as e:
        import traceback
        error_msg = f"Error al procesar la imagen: {str(e)}\n{traceback.format_exc()}"
        print(f"\n❌ {error_msg}")
        return {"error": error_msg}


def analizar_color_labios(ruta_imagen):
    """
    Analiza el color de labios de una imagen
    
    Args:
        ruta_imagen: Ruta al archivo de imagen
        
    Returns:
        dict con el resultado del análisis
    """
    print("\n" + "="*60)
    print("💄 ANÁLISIS DE COLOR DE LABIOS")
    print("="*60)
    
    try:
        if not os.path.exists(ruta_imagen):
            return {"error": f"Archivo no encontrado: {ruta_imagen}"}
        
        print(f"📁 Procesando: {ruta_imagen}")
        print("⏳ Extrayendo códigos RGB de labios...")
        
        # Extraer códigos RGB
        rgb_codes = f.get_rgb_codes(ruta_imagen)
        
        print(f"📊 {len(rgb_codes)} píxeles de labios detectados")
        print("🎲 Seleccionando muestra aleatoria de 40 píxeles...")
        
        # Filtrar y seleccionar muestra aleatoria
        random_rgb_codes = f.filter_lip_random(rgb_codes, 40)
        
        print("🧮 Calculando distancias a paletas de referencia...")
        
        # Calcular distancias
        types = Counter(f.calc_dis(random_rgb_codes))
        
        print(f"📈 Distribución: {dict(types)}")
        
        # Obtener el tipo más común
        max_value_key = max(types, key=types.get)
        
        # Mapear a código numérico
        type_mapping = {
            'sp': 1,
            'su': 2,
            'au': 3,
            'win': 4
        }
        
        result = type_mapping.get(max_value_key, 0)
        
        # Nombres de temporadas
        season_names = {
            1: "Spring (Primavera)",
            2: "Summer (Verano)",
            3: "Autumn (Otoño)",
            4: "Winter (Invierno)"
        }
        
        season_descriptions = {
            1: "Labios con tonos cálidos - Recomendado: corales, melocotones, rojos anaranjados",
            2: "Labios con tonos fríos suaves - Recomendado: rosas, malvas, rojos azulados suaves",
            3: "Labios con tonos cálidos profundos - Recomendado: terracota, vino, marrones",
            4: "Labios con tonos fríos intensos - Recomendado: rojos puros, fucsias, berries"
        }
        
        resultado = {
            "codigo": result,
            "temporada": season_names.get(result, "Desconocido"),
            "tipo_analisis": max_value_key,
            "descripcion": season_descriptions.get(result, ""),
            "distribucion": dict(types)
        }
        
        print("\n✅ RESULTADO:")
        print(f"   🎯 Temporada: {resultado['temporada']}")
        print(f"   📊 Código: {resultado['codigo']}")
        print(f"   🔍 Tipo: {resultado['tipo_analisis']}")
        print(f"   💡 Descripción: {resultado['descripcion']}")
        
        return resultado
        
    except Exception as e:
        import traceback
        error_msg = f"Error al procesar la imagen: {str(e)}\n{traceback.format_exc()}"
        print(f"\n❌ {error_msg}")
        return {"error": error_msg}


def analizar_completo(ruta_imagen):
    """
    Realiza análisis completo: tono de piel y color de labios
    
    Args:
        ruta_imagen: Ruta al archivo de imagen
    """
    print("\n" + "🌟"*30)
    print("   COLORINSIGHT - ANÁLISIS COMPLETO DE COLOR PERSONAL")
    print("🌟"*30)
    print(f"\n📷 Imagen: {ruta_imagen}\n")
    
    # Análisis de tono de piel
    resultado_piel = analizar_tono_piel(ruta_imagen)
    
    # Análisis de color de labios
    resultado_labios = analizar_color_labios(ruta_imagen)
    
    # Resumen final
    print("\n" + "="*60)
    print("📋 RESUMEN FINAL")
    print("="*60)
    
    if "error" not in resultado_piel:
        print(f"🎨 Tono de Piel: {resultado_piel['temporada']}")
    else:
        print(f"🎨 Tono de Piel: Error en análisis")
    
    if "error" not in resultado_labios:
        print(f"💄 Color de Labios: {resultado_labios['temporada']}")
    else:
        print(f"💄 Color de Labios: Error en análisis")
    
    print("\n" + "="*60)
    print("✨ Análisis completado")
    print("="*60 + "\n")
    
    return {
        "tono_piel": resultado_piel,
        "color_labios": resultado_labios
    }


def main():
    """
    Función principal para ejecutar desde línea de comandos
    """
    parser = argparse.ArgumentParser(
        description="ColorInsight - Análisis de Color Personal (Versión Local)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Análisis completo (piel + labios)
  python colorInsight.py "C:/Users/foto.jpg"
  
  # Solo análisis de tono de piel
  python colorInsight.py "C:/Users/foto.jpg" --skin
  
  # Solo análisis de color de labios
  python colorInsight.py "C:/Users/foto.jpg" --lip
        """
    )
    
    parser.add_argument(
        'imagen',
        type=str,
        help='Ruta al archivo de imagen a analizar'
    )
    
    parser.add_argument(
        '--skin',
        action='store_true',
        help='Realizar solo análisis de tono de piel'
    )
    
    parser.add_argument(
        '--lip',
        action='store_true',
        help='Realizar solo análisis de color de labios'
    )
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Verificar que la imagen existe
    if not os.path.exists(args.imagen):
        print(f"❌ Error: No se encuentra el archivo '{args.imagen}'")
        sys.exit(1)
    
    # Ejecutar análisis según las opciones
    if args.skin:
        analizar_tono_piel(args.imagen)
    elif args.lip:
        analizar_color_labios(args.imagen)
    else:
        # Por defecto, análisis completo
        analizar_completo(args.imagen)


if __name__ == "__main__":
    main()
