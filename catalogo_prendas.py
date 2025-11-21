# Catálogo de prendas con colorimetría personal
# Basado en el análisis de temporadas de color:
# 1: Spring (Primavera) - Tonos cálidos y brillantes
# 2: Summer (Verano) - Tonos fríos y suaves  
# 3: Autumn (Otoño) - Tonos cálidos y profundos
# 4: Winter (Invierno) - Tonos fríos e intensos

# ========== CAMISAS ==========
prendas_camisas = [
    # Spring - Colores cálidos y brillantes (coral, melocotón, amarillo claro, verde claro)
    {"nombre": "Camisa Coral Primavera Talla S", "tipo": "camisa", "color": "Coral", "season": "Spring", 
     "medidas": {"pecho": 92, "cintura": 78, "ancho_hombros": 43, "largo_brazo": 61, "cuello": 37}},
    {"nombre": "Camisa Melocotón Primavera Talla M", "tipo": "camisa", "color": "Peach", "season": "Spring",
     "medidas": {"pecho": 100, "cintura": 86, "ancho_hombros": 46, "largo_brazo": 63, "cuello": 39}},
    {"nombre": "Camisa Verde Claro Primavera Talla L", "tipo": "camisa", "color": "Light Green", "season": "Spring",
     "medidas": {"pecho": 108, "cintura": 94, "ancho_hombros": 49, "largo_brazo": 65, "cuello": 41}},
    
    # Summer - Colores fríos y suaves (azul polvo, lavanda, rosa suave, gris azulado)
    {"nombre": "Camisa Lavanda Verano Talla S", "tipo": "camisa", "color": "Lavender", "season": "Summer",
     "medidas": {"pecho": 92, "cintura": 78, "ancho_hombros": 43, "largo_brazo": 61, "cuello": 37}},
    {"nombre": "Camisa Azul Polvo Verano Talla M", "tipo": "camisa", "color": "Powder Blue", "season": "Summer",
     "medidas": {"pecho": 100, "cintura": 86, "ancho_hombros": 46, "largo_brazo": 63, "cuello": 39}},
    {"nombre": "Camisa Rosa Suave Verano Talla L", "tipo": "camisa", "color": "Soft Pink", "season": "Summer",
     "medidas": {"pecho": 108, "cintura": 94, "ancho_hombros": 49, "largo_brazo": 65, "cuello": 41}},
    
    # Autumn - Colores cálidos y profundos (terracota, mostaza, marrón, verde oliva)
    {"nombre": "Camisa Terracota Otoño Talla S", "tipo": "camisa", "color": "Terracotta", "season": "Autumn",
     "medidas": {"pecho": 92, "cintura": 78, "ancho_hombros": 43, "largo_brazo": 61, "cuello": 37}},
    {"nombre": "Camisa Mostaza Otoño Talla M", "tipo": "camisa", "color": "Mustard", "season": "Autumn",
     "medidas": {"pecho": 100, "cintura": 86, "ancho_hombros": 46, "largo_brazo": 63, "cuello": 39}},
    {"nombre": "Camisa Verde Oliva Otoño Talla L", "tipo": "camisa", "color": "Olive Green", "season": "Autumn",
     "medidas": {"pecho": 108, "cintura": 94, "ancho_hombros": 49, "largo_brazo": 65, "cuello": 41}},
    
    # Winter - Colores fríos e intensos (negro, blanco puro, azul real, rojo intenso)
    {"nombre": "Camisa Blanca Pura Invierno Talla S", "tipo": "camisa", "color": "Pure White", "season": "Winter",
     "medidas": {"pecho": 92, "cintura": 78, "ancho_hombros": 43, "largo_brazo": 61, "cuello": 37}},
    {"nombre": "Camisa Azul Real Invierno Talla M", "tipo": "camisa", "color": "Royal Blue", "season": "Winter",
     "medidas": {"pecho": 100, "cintura": 86, "ancho_hombros": 46, "largo_brazo": 63, "cuello": 39}},
    {"nombre": "Camisa Negra Invierno Talla L", "tipo": "camisa", "color": "Black", "season": "Winter",
     "medidas": {"pecho": 108, "cintura": 94, "ancho_hombros": 49, "largo_brazo": 65, "cuello": 41}},
]

# ========== PANTALONES ==========
prendas_pantalones = [
    # Spring - Tonos cálidos y claros
    {"nombre": "Pantalón Beige Claro Primavera Talla 30", "tipo": "pantalón", "color": "Light Beige", "season": "Spring",
     "medidas": {"cintura": 78, "cadera": 90, "muslo": 52, "tobillo": 19, "altura": 170}},
    {"nombre": "Pantalón Camel Primavera Talla 32", "tipo": "pantalón", "color": "Camel", "season": "Spring",
     "medidas": {"cintura": 84, "cadera": 96, "muslo": 56, "tobillo": 21, "altura": 175}},
    {"nombre": "Pantalón Verde Menta Primavera Talla 34", "tipo": "pantalón", "color": "Mint Green", "season": "Spring",
     "medidas": {"cintura": 90, "cadera": 102, "muslo": 60, "tobillo": 22, "altura": 180}},
    
    # Summer - Tonos fríos suaves
    {"nombre": "Pantalón Gris Claro Verano Talla 30", "tipo": "pantalón", "color": "Light Gray", "season": "Summer",
     "medidas": {"cintura": 78, "cadera": 90, "muslo": 52, "tobillo": 19, "altura": 170}},
    {"nombre": "Pantalón Azul Marino Suave Verano Talla 32", "tipo": "pantalón", "color": "Soft Navy", "season": "Summer",
     "medidas": {"cintura": 84, "cadera": 96, "muslo": 56, "tobillo": 21, "altura": 175}},
    {"nombre": "Pantalón Malva Verano Talla 34", "tipo": "pantalón", "color": "Mauve", "season": "Summer",
     "medidas": {"cintura": 90, "cadera": 102, "muslo": 60, "tobillo": 22, "altura": 180}},
    
    # Autumn - Tonos tierra profundos
    {"nombre": "Pantalón Marrón Chocolate Otoño Talla 30", "tipo": "pantalón", "color": "Chocolate Brown", "season": "Autumn",
     "medidas": {"cintura": 78, "cadera": 90, "muslo": 52, "tobillo": 19, "altura": 170}},
    {"nombre": "Pantalón Óxido Otoño Talla 32", "tipo": "pantalón", "color": "Rust", "season": "Autumn",
     "medidas": {"cintura": 84, "cadera": 96, "muslo": 56, "tobillo": 21, "altura": 175}},
    {"nombre": "Pantalón Caqui Otoño Talla 34", "tipo": "pantalón", "color": "Khaki", "season": "Autumn",
     "medidas": {"cintura": 90, "cadera": 102, "muslo": 60, "tobillo": 22, "altura": 180}},
    
    # Winter - Tonos contrastantes e intensos
    {"nombre": "Pantalón Negro Invierno Talla 30", "tipo": "pantalón", "color": "Black", "season": "Winter",
     "medidas": {"cintura": 78, "cadera": 90, "muslo": 52, "tobillo": 19, "altura": 170}},
    {"nombre": "Pantalón Gris Carbón Invierno Talla 32", "tipo": "pantalón", "color": "Charcoal Gray", "season": "Winter",
     "medidas": {"cintura": 84, "cadera": 96, "muslo": 56, "tobillo": 21, "altura": 175}},
    {"nombre": "Pantalón Azul Marino Intenso Invierno Talla 34", "tipo": "pantalón", "color": "Deep Navy", "season": "Winter",
     "medidas": {"cintura": 90, "cadera": 102, "muslo": 60, "tobillo": 22, "altura": 180}},
]

# ========== CHAQUETAS ==========
prendas_chaquetas = [
    # Spring - Colores vivos y cálidos
    {"nombre": "Chaqueta Amarillo Mantequilla Primavera Talla S", "tipo": "chaqueta", "color": "Butter Yellow", "season": "Spring",
     "medidas": {"pecho": 96, "cintura": 82, "ancho_hombros": 44, "largo_brazo": 62, "cuello": 38}},
    {"nombre": "Chaqueta Coral Primavera Talla M", "tipo": "chaqueta", "color": "Coral", "season": "Spring",
     "medidas": {"pecho": 104, "cintura": 90, "ancho_hombros": 47, "largo_brazo": 64, "cuello": 40}},
    {"nombre": "Chaqueta Turquesa Claro Primavera Talla L", "tipo": "chaqueta", "color": "Light Turquoise", "season": "Spring",
     "medidas": {"pecho": 110, "cintura": 98, "ancho_hombros": 50, "largo_brazo": 66, "cuello": 42}},
    
    # Summer - Colores pasteles fríos
    {"nombre": "Chaqueta Rosa Empolvado Verano Talla S", "tipo": "chaqueta", "color": "Dusty Rose", "season": "Summer",
     "medidas": {"pecho": 96, "cintura": 82, "ancho_hombros": 44, "largo_brazo": 62, "cuello": 38}},
    {"nombre": "Chaqueta Azul Cielo Verano Talla M", "tipo": "chaqueta", "color": "Sky Blue", "season": "Summer",
     "medidas": {"pecho": 104, "cintura": 90, "ancho_hombros": 47, "largo_brazo": 64, "cuello": 40}},
    {"nombre": "Chaqueta Gris Perla Verano Talla L", "tipo": "chaqueta", "color": "Pearl Gray", "season": "Summer",
     "medidas": {"pecho": 110, "cintura": 98, "ancho_hombros": 50, "largo_brazo": 66, "cuello": 42}},
    
    # Autumn - Tonos tierra ricos
    {"nombre": "Chaqueta Caoba Otoño Talla S", "tipo": "chaqueta", "color": "Mahogany", "season": "Autumn",
     "medidas": {"pecho": 96, "cintura": 82, "ancho_hombros": 44, "largo_brazo": 62, "cuello": 38}},
    {"nombre": "Chaqueta Naranja Quemado Otoño Talla M", "tipo": "chaqueta", "color": "Burnt Orange", "season": "Autumn",
     "medidas": {"pecho": 104, "cintura": 90, "ancho_hombros": 47, "largo_brazo": 64, "cuello": 40}},
    {"nombre": "Chaqueta Verde Bosque Otoño Talla L", "tipo": "chaqueta", "color": "Forest Green", "season": "Autumn",
     "medidas": {"pecho": 110, "cintura": 98, "ancho_hombros": 50, "largo_brazo": 66, "cuello": 42}},
    
    # Winter - Colores dramáticos
    {"nombre": "Chaqueta Rojo Intenso Invierno Talla S", "tipo": "chaqueta", "color": "True Red", "season": "Winter",
     "medidas": {"pecho": 96, "cintura": 82, "ancho_hombros": 44, "largo_brazo": 62, "cuello": 38}},
    {"nombre": "Chaqueta Blanco Hielo Invierno Talla M", "tipo": "chaqueta", "color": "Ice White", "season": "Winter",
     "medidas": {"pecho": 104, "cintura": 90, "ancho_hombros": 47, "largo_brazo": 64, "cuello": 40}},
    {"nombre": "Chaqueta Negro Azabache Invierno Talla L", "tipo": "chaqueta", "color": "Jet Black", "season": "Winter",
     "medidas": {"pecho": 110, "cintura": 98, "ancho_hombros": 50, "largo_brazo": 66, "cuello": 42}},
]

# ========== POLERAS ==========
prendas_poleras = [
    # Spring - Colores alegres y luminosos
    {"nombre": "Polera Salmón Primavera Talla S", "tipo": "polera", "color": "Salmon", "season": "Spring",
     "medidas": {"pecho": 90, "cintura": 76, "ancho_hombros": 42, "altura": 165}},
    {"nombre": "Polera Amarillo Limón Primavera Talla M", "tipo": "polera", "color": "Lemon Yellow", "season": "Spring",
     "medidas": {"pecho": 98, "cintura": 84, "ancho_hombros": 45, "altura": 172}},
    {"nombre": "Polera Verde Pistacho Primavera Talla L", "tipo": "polera", "color": "Pistachio Green", "season": "Spring",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "altura": 178}},
    
    # Summer - Tonos pastel suaves
    {"nombre": "Polera Lila Suave Verano Talla S", "tipo": "polera", "color": "Soft Lilac", "season": "Summer",
     "medidas": {"pecho": 90, "cintura": 76, "ancho_hombros": 42, "altura": 165}},
    {"nombre": "Polera Aqua Verano Talla M", "tipo": "polera", "color": "Aqua", "season": "Summer",
     "medidas": {"pecho": 98, "cintura": 84, "ancho_hombros": 45, "altura": 172}},
    {"nombre": "Polera Gris Azulado Verano Talla L", "tipo": "polera", "color": "Blue Gray", "season": "Summer",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "altura": 178}},
    
    # Autumn - Colores especiados y terrosos
    {"nombre": "Polera Canela Otoño Talla S", "tipo": "polera", "color": "Cinnamon", "season": "Autumn",
     "medidas": {"pecho": 90, "cintura": 76, "ancho_hombros": 42, "altura": 165}},
    {"nombre": "Polera Bronce Otoño Talla M", "tipo": "polera", "color": "Bronze", "season": "Autumn",
     "medidas": {"pecho": 98, "cintura": 84, "ancho_hombros": 45, "altura": 172}},
    {"nombre": "Polera Burdeos Otoño Talla L", "tipo": "polera", "color": "Burgundy", "season": "Autumn",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "altura": 178}},
    
    # Winter - Colores puros y contrastantes
    {"nombre": "Polera Blanco Nieve Invierno Talla S", "tipo": "polera", "color": "Snow White", "season": "Winter",
     "medidas": {"pecho": 90, "cintura": 76, "ancho_hombros": 42, "altura": 165}},
    {"nombre": "Polera Fucsia Invierno Talla M", "tipo": "polera", "color": "Fuchsia", "season": "Winter",
     "medidas": {"pecho": 98, "cintura": 84, "ancho_hombros": 45, "altura": 172}},
    {"nombre": "Polera Azul Eléctrico Invierno Talla L", "tipo": "polera", "color": "Electric Blue", "season": "Winter",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "altura": 178}},
]

# ========== SUÉTERES ==========
prendas_sueteres = [
    # Spring
    {"nombre": "Suéter Durazno Primavera Talla S", "tipo": "suéter", "color": "Peach", "season": "Spring",
     "medidas": {"pecho": 94, "cintura": 80, "ancho_hombros": 44, "largo_brazo": 62}},
    {"nombre": "Suéter Verde Agua Primavera Talla M", "tipo": "suéter", "color": "Aqua Green", "season": "Spring",
     "medidas": {"pecho": 102, "cintura": 88, "ancho_hombros": 47, "largo_brazo": 64}},
    
    # Summer
    {"nombre": "Suéter Azul Grisáceo Verano Talla S", "tipo": "suéter", "color": "Blue Gray", "season": "Summer",
     "medidas": {"pecho": 94, "cintura": 80, "ancho_hombros": 44, "largo_brazo": 62}},
    {"nombre": "Suéter Lavanda Claro Verano Talla M", "tipo": "suéter", "color": "Light Lavender", "season": "Summer",
     "medidas": {"pecho": 102, "cintura": 88, "ancho_hombros": 47, "largo_brazo": 64}},
    
    # Autumn
    {"nombre": "Suéter Caramelo Otoño Talla S", "tipo": "suéter", "color": "Caramel", "season": "Autumn",
     "medidas": {"pecho": 94, "cintura": 80, "ancho_hombros": 44, "largo_brazo": 62}},
    {"nombre": "Suéter Ocre Otoño Talla M", "tipo": "suéter", "color": "Ochre", "season": "Autumn",
     "medidas": {"pecho": 102, "cintura": 88, "ancho_hombros": 47, "largo_brazo": 64}},
    
    # Winter
    {"nombre": "Suéter Púrpura Real Invierno Talla S", "tipo": "suéter", "color": "Royal Purple", "season": "Winter",
     "medidas": {"pecho": 94, "cintura": 80, "ancho_hombros": 44, "largo_brazo": 62}},
    {"nombre": "Suéter Negro Profundo Invierno Talla M", "tipo": "suéter", "color": "Deep Black", "season": "Winter",
     "medidas": {"pecho": 102, "cintura": 88, "ancho_hombros": 47, "largo_brazo": 64}},
]

# ========== VESTIDOS ==========
prendas_vestidos = [
    # Spring
    {"nombre": "Vestido Coral Brillante Primavera Talla S", "tipo": "vestido", "color": "Bright Coral", "season": "Spring",
     "medidas": {"pecho": 88, "cintura": 72, "cadera": 94, "altura": 165}},
    {"nombre": "Vestido Amarillo Sol Primavera Talla M", "tipo": "vestido", "color": "Sunflower Yellow", "season": "Spring",
     "medidas": {"pecho": 96, "cintura": 80, "cadera": 102, "altura": 170}},
    
    # Summer
    {"nombre": "Vestido Rosa Empolvado Verano Talla S", "tipo": "vestido", "color": "Dusty Pink", "season": "Summer",
     "medidas": {"pecho": 88, "cintura": 72, "cadera": 94, "altura": 165}},
    {"nombre": "Vestido Azul Serenidad Verano Talla M", "tipo": "vestido", "color": "Serenity Blue", "season": "Summer",
     "medidas": {"pecho": 96, "cintura": 80, "cadera": 102, "altura": 170}},
    
    # Autumn
    {"nombre": "Vestido Burdeos Profundo Otoño Talla S", "tipo": "vestido", "color": "Deep Burgundy", "season": "Autumn",
     "medidas": {"pecho": 88, "cintura": 72, "cadera": 94, "altura": 165}},
    {"nombre": "Vestido Verde Musgo Otoño Talla M", "tipo": "vestido", "color": "Moss Green", "season": "Autumn",
     "medidas": {"pecho": 96, "cintura": 80, "cadera": 102, "altura": 170}},
    
    # Winter
    {"nombre": "Vestido Esmeralda Invierno Talla S", "tipo": "vestido", "color": "Emerald", "season": "Winter",
     "medidas": {"pecho": 88, "cintura": 72, "cadera": 94, "altura": 165}},
    {"nombre": "Vestido Magenta Invierno Talla M", "tipo": "vestido", "color": "Magenta", "season": "Winter",
     "medidas": {"pecho": 96, "cintura": 80, "cadera": 102, "altura": 170}},
]

# ========== ABRIGOS ==========
prendas_abrigos = [
    # Spring
    {"nombre": "Abrigo Beige Cálido Primavera Talla M", "tipo": "abrigo", "color": "Warm Beige", "season": "Spring",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "largo_brazo": 65}},
    
    # Summer
    {"nombre": "Abrigo Gris Perla Verano Talla M", "tipo": "abrigo", "color": "Pearl Gray", "season": "Summer",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "largo_brazo": 65}},
    
    # Autumn
    {"nombre": "Abrigo Camel Profundo Otoño Talla M", "tipo": "abrigo", "color": "Deep Camel", "season": "Autumn",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "largo_brazo": 65}},
    
    # Winter
    {"nombre": "Abrigo Gris Antracita Invierno Talla M", "tipo": "abrigo", "color": "Anthracite Gray", "season": "Winter",
     "medidas": {"pecho": 106, "cintura": 92, "ancho_hombros": 48, "largo_brazo": 65}},
]

catalogo_prendas = (prendas_camisas + prendas_pantalones + prendas_chaquetas + 
                   prendas_poleras + prendas_sueteres + prendas_vestidos + prendas_abrigos)
