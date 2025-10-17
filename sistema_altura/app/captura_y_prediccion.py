#!/usr/bin/env python3
"""
Sistema de Captura y Predicción de Estatura
===========================================

Aplicación con interfaz gráfica para:
1. Capturar fotos con la cámara web
2. Verificar distancia óptima (2.5m)
3. Procesar la imagen con el modelo
4. Predecir la estatura automáticamente
5. Guardar resultados con historial

Autor: Sistema de Estimación de Estatura
Fecha: 15 de octubre de 2025
"""

import cv2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
import joblib  # Cambiado de pickle a joblib para compatibilidad
import json
import os
from datetime import datetime
import threading
from pathlib import Path


class SistemaCapturaPrediccion:
    """Sistema completo de captura de fotos y predicción de estatura"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Captura y Predicción de Estatura")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Variables de estado
        self.captura_activa = False
        self.camera = None
        self.current_frame = None
        self.modelo = None
        self.scaler = None
        self.metadata = None
        self.calibracion = None  # Calibración con datos reales
        self.mp_pose = mp.solutions.pose
        self.pose = None
        self.ultima_prediccion = None
        
        # Configuración
        self.DISTANCIA_OPTIMA = 2.5  # metros
        self.DISTANCIA_MIN = 1.5
        self.DISTANCIA_MAX = 4.0
        self.directorio_capturas = "capturas_estatura"
        self.directorio_resultados = "resultados_predicciones"
        
        # Crear directorios
        Path(self.directorio_capturas).mkdir(exist_ok=True)
        Path(self.directorio_resultados).mkdir(exist_ok=True)
        
        # Cargar modelo automáticamente
        self.cargar_modelo_automatico()
        
        # Configurar interfaz
        self.configurar_interfaz()
        
        # Iniciar MediaPipe
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def configurar_interfaz(self):
        """Configura toda la interfaz gráfica"""
        
        # Título principal
        titulo_frame = tk.Frame(self.root, bg='#34495e', height=80)
        titulo_frame.pack(fill='x', padx=10, pady=10)
        titulo_frame.pack_propagate(False)
        
        titulo_label = tk.Label(
            titulo_frame,
            text="📸 Sistema de Captura y Predicción de Estatura 📏",
            font=('Arial', 24, 'bold'),
            bg='#34495e',
            fg='white'
        )
        titulo_label.pack(expand=True)
        
        # Frame principal con dos columnas
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ===== COLUMNA IZQUIERDA: Cámara y controles =====
        left_frame = tk.Frame(main_frame, bg='#34495e', relief='ridge', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Frame de video
        video_label_frame = tk.LabelFrame(
            left_frame,
            text="📹 Vista de Cámara",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white',
            relief='solid',
            bd=2
        )
        video_label_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.video_label = tk.Label(
            video_label_frame,
            bg='black',
            text="Cámara no iniciada\n\nPresiona 'Iniciar Cámara'",
            fg='white',
            font=('Arial', 16)
        )
        self.video_label.pack(padx=5, pady=5, fill='both', expand=True)
        
        # Información de distancia
        distancia_frame = tk.Frame(left_frame, bg='#34495e')
        distancia_frame.pack(fill='x', padx=10, pady=5)
        
        self.distancia_label = tk.Label(
            distancia_frame,
            text=f"⚠️ IMPORTANTE: Coloque a la persona a {self.DISTANCIA_OPTIMA}m de distancia",
            font=('Arial', 12, 'bold'),
            bg='#f39c12',
            fg='white',
            relief='solid',
            bd=2,
            pady=10
        )
        self.distancia_label.pack(fill='x', pady=5)
        
        # Controles de cámara
        controles_frame = tk.Frame(left_frame, bg='#34495e')
        controles_frame.pack(fill='x', padx=10, pady=10)
        
        self.btn_iniciar_camara = tk.Button(
            controles_frame,
            text="▶️ Iniciar Cámara",
            command=self.iniciar_camara,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_iniciar_camara.pack(side='left', padx=5, expand=True, fill='x')
        
        self.btn_capturar = tk.Button(
            controles_frame,
            text="📸 Capturar Foto",
            command=self.capturar_foto,
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            state='disabled',
            cursor='hand2'
        )
        self.btn_capturar.pack(side='left', padx=5, expand=True, fill='x')
        
        self.btn_detener = tk.Button(
            controles_frame,
            text="⏹️ Detener Cámara",
            command=self.detener_camara,
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            state='disabled',
            cursor='hand2'
        )
        self.btn_detener.pack(side='left', padx=5, expand=True, fill='x')
        
        # ===== COLUMNA DERECHA: Resultados e información =====
        right_frame = tk.Frame(main_frame, bg='#34495e', relief='ridge', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Estado del modelo
        modelo_frame = tk.LabelFrame(
            right_frame,
            text="🤖 Estado del Modelo",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            relief='solid',
            bd=2
        )
        modelo_frame.pack(fill='x', padx=10, pady=10)
        
        modelo_color = '#27ae60' if self.modelo else '#e74c3c'
        modelo_texto = '✅ Modelo cargado' if self.modelo else '❌ Modelo no encontrado'
        
        self.modelo_label = tk.Label(
            modelo_frame,
            text=modelo_texto,
            font=('Arial', 11),
            bg=modelo_color,
            fg='white',
            pady=8
        )
        self.modelo_label.pack(fill='x', padx=5, pady=5)
        
        if self.metadata:
            info_modelo = f"Modelo: {self.metadata.get('model_name', 'N/A')}\n"
            info_modelo += f"Precisión: MAE = {self.metadata.get('test_metrics', {}).get('mae', 0):.2f} cm"
            tk.Label(
                modelo_frame,
                text=info_modelo,
                font=('Arial', 9),
                bg='#34495e',
                fg='white',
                justify='left'
            ).pack(anchor='w', padx=10, pady=3)
        
        # Guía de captura
        guia_frame = tk.LabelFrame(
            right_frame,
            text="📋 Guía de Captura",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            relief='solid',
            bd=2
        )
        guia_frame.pack(fill='x', padx=10, pady=10)
        
        guia_texto = """
✅ Distancia: 2.0m - 3.0m (ideal 2.5m)
✅ Cámara estable (trípode recomendado)
✅ Altura de cámara: 1.2-1.4m del suelo
✅ Persona de pie, erguida
✅ Brazos relajados a los lados
✅ Vista frontal completa
✅ Fondo despejado y contrastante
✅ Iluminación uniforme
✅ Persona ocupa 70-90% del encuadre
        """
        
        tk.Label(
            guia_frame,
            text=guia_texto,
            font=('Arial', 10),
            bg='#34495e',
            fg='white',
            justify='left',
            anchor='w'
        ).pack(padx=10, pady=5, fill='x')
        
        # Resultados de predicción
        resultados_frame = tk.LabelFrame(
            right_frame,
            text="📊 Última Predicción",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            relief='solid',
            bd=2
        )
        resultados_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.resultados_text = tk.Text(
            resultados_frame,
            font=('Courier', 11),
            bg='#2c3e50',
            fg='#ecf0f1',
            relief='sunken',
            bd=2,
            wrap='word',
            height=12
        )
        self.resultados_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Mensaje inicial
        self.resultados_text.insert('1.0', 
            "Esperando captura...\n\n"
            "1️⃣ Inicia la cámara\n"
            "2️⃣ Coloca a la persona a 2.5m\n"
            "3️⃣ Captura la foto\n"
            "4️⃣ Obtén la predicción automáticamente"
        )
        self.resultados_text.config(state='disabled')
        
        # Botones adicionales
        botones_frame = tk.Frame(right_frame, bg='#34495e')
        botones_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            botones_frame,
            text="📂 Cargar Imagen",
            command=self.cargar_imagen_externa,
            font=('Arial', 11, 'bold'),
            bg='#9b59b6',
            fg='white',
            relief='raised',
            bd=2,
            padx=10,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        tk.Button(
            botones_frame,
            text="📁 Ver Capturas",
            command=self.abrir_carpeta_capturas,
            font=('Arial', 11, 'bold'),
            bg='#16a085',
            fg='white',
            relief='raised',
            bd=2,
            padx=10,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        tk.Button(
            botones_frame,
            text="📊 Ver Resultados",
            command=self.abrir_carpeta_resultados,
            font=('Arial', 11, 'bold'),
            bg='#d35400',
            fg='white',
            relief='raised',
            bd=2,
            padx=10,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        # Barra de estado
        self.status_bar = tk.Label(
            self.root,
            text="Estado: Listo | Modelo cargado ✅" if self.modelo else "Estado: Modelo no encontrado ❌",
            font=('Arial', 10),
            bg='#1abc9c' if self.modelo else '#e74c3c',
            fg='white',
            anchor='w',
            relief='sunken',
            bd=1,
            padx=10,
            pady=5
        )
        self.status_bar.pack(side='bottom', fill='x')
        
    def cargar_modelo_automatico(self):
        """Carga automáticamente el modelo más reciente"""
        try:
            # Buscar archivos de modelo en el directorio 'app' y en la carpeta 'modelos' del proyecto
            import os
            app_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'

            modelos = list(Path(app_dir).glob('modelo_altura_*.pkl'))

            # Si no hay modelos en app/, buscar en ../modelos (raíz del proyecto)
            if not modelos:
                project_root = Path(app_dir).parent
                modelos_dir = project_root / 'modelos'
                print(f"ℹ️  No se encontraron modelos en {app_dir}. Buscando en {modelos_dir}...")
                if modelos_dir.exists():
                    modelos = list(modelos_dir.glob('modelo_altura_*.pkl'))

            if not modelos:
                print("⚠️ No se encontraron modelos entrenados")
                print(f"   Buscando en: {app_dir}")
                print(f"   También se buscó en: {str(project_root / 'modelos')}")
                print("   Por favor, entrena el modelo primero con: python train_height_model.py o coloca el .pkl en la carpeta modelos/")
                return False
            
            # Usar el más reciente
            modelo_path = max(modelos, key=lambda p: p.stat().st_mtime)
            
            # Extraer timestamp (últimas 2 partes: fecha_hora)
            parts = modelo_path.stem.split('_')
            timestamp = '_'.join(parts[-2:])
            
            print(f"📂 Cargando modelo: {modelo_path.name}")
            
            # Cargar modelo (usando joblib en lugar de pickle)
            self.modelo = joblib.load(modelo_path)
            
            # Cargar scaler (corregido: sin "altura_" en el nombre)
            # Intentar localizar scaler/metadata/calibracion en el mismo directorio donde se encontró el modelo
            scaler_path = modelo_path.parent / f'scaler_{timestamp}.pkl'
            if not scaler_path.exists():
                # Intentar con nombre alternativo
                scaler_path = modelo_path.parent / f'scaler_altura_{timestamp}.pkl'
            
            print(f"📂 Cargando scaler: {scaler_path.name}")
            self.scaler = joblib.load(scaler_path)
            
            # Cargar metadata (corregido: sin "altura_" extra)
            metadata_path = modelo_path.parent / f'modelo_metadata_{timestamp}.json'
            if not metadata_path.exists():
                # Intentar con nombre alternativo
                metadata_path = modelo_path.parent / f'modelo_altura_{timestamp}.json'
            
            print(f"📂 Cargando metadata: {metadata_path.name}")
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            # Cargar calibración si existe
            self.calibracion = None
            calibracion_path = modelo_path.parent / f'calibracion_{timestamp}.json'
            if calibracion_path.exists():
                print(f"📂 Cargando calibración: {calibracion_path.name}")
                with open(calibracion_path, 'r') as f:
                    self.calibracion = json.load(f)
                print(f"   ✅ Calibración aplicada (offset: {self.calibracion['offset_aditivo']:+.2f} cm)")
            else:
                print(f"   ℹ️  Sin calibración (usa 'python calibrar_modelo.py' para mejorar precisión)")
            
            print(f"✅ Modelo cargado exitosamente")
            print(f"   Modelo: {self.metadata.get('model_name', 'N/A')}")
            print(f"   MAE: {self.metadata.get('test_metrics', {}).get('mae', 0):.2f} cm")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar modelo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def iniciar_camara(self):
        """Inicia la captura de video de la cámara"""
        if self.captura_activa:
            return
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
                return
            
            # Configurar resolución
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.captura_activa = True
            self.btn_iniciar_camara.config(state='disabled')
            self.btn_capturar.config(state='normal')
            self.btn_detener.config(state='normal')
            self.status_bar.config(text="Estado: Cámara activa 📹", bg='#27ae60')
            
            # Iniciar thread de actualización
            self.actualizar_video()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar cámara: {e}")
    
    def actualizar_video(self):
        """Actualiza el frame de video continuamente"""
        if not self.captura_activa:
            return
        
        try:
            ret, frame = self.camera.read()
            if ret:
                # Procesar con MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(frame_rgb)
                
                # Dibujar landmarks
                if results.pose_landmarks:
                    self.dibujar_guias(frame, results.pose_landmarks)
                    
                    # Verificar calidad de detección
                    visibility = self.calcular_visibilidad(results.pose_landmarks)
                    if visibility > 0.9:
                        cv2.putText(frame, "Deteccion: EXCELENTE", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    elif visibility > 0.7:
                        cv2.putText(frame, "Deteccion: BUENA", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame, "Deteccion: MEJORAR", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "No se detecta persona completa", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Añadir guía de distancia
                self.dibujar_guia_distancia(frame)
                
                # Guardar frame actual
                self.current_frame = frame.copy()
                
                # Convertir para Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            
            # Continuar actualización
            self.root.after(30, self.actualizar_video)
            
        except Exception as e:
            print(f"Error en actualización de video: {e}")
    
    def dibujar_guias(self, frame, landmarks):
        """Dibuja guías y landmarks en el frame"""
        h, w = frame.shape[:2]
        
        # Dibujar landmarks principales
        for idx, landmark in enumerate(landmarks.landmark):
            if landmark.visibility > 0.5:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
        
        # Dibujar líneas de conexión principales
        conexiones = [
            (11, 12),  # Hombros
            (11, 23),  # Hombro izq - cadera izq
            (12, 24),  # Hombro der - cadera der
            (23, 24),  # Caderas
            (23, 25),  # Cadera izq - rodilla izq
            (24, 26),  # Cadera der - rodilla der
            (25, 27),  # Rodilla izq - tobillo izq
            (26, 28),  # Rodilla der - tobillo der
        ]
        
        for start, end in conexiones:
            if (landmarks.landmark[start].visibility > 0.5 and 
                landmarks.landmark[end].visibility > 0.5):
                x1 = int(landmarks.landmark[start].x * w)
                y1 = int(landmarks.landmark[start].y * h)
                x2 = int(landmarks.landmark[end].x * w)
                y2 = int(landmarks.landmark[end].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    def dibujar_guia_distancia(self, frame):
        """Dibuja guía de distancia óptima en el frame"""
        h, w = frame.shape[:2]
        
        # Rectángulo de área óptima (70-90% del alto)
        margen_arriba = int(h * 0.05)
        margen_abajo = int(h * 0.05)
        margen_lados = int(w * 0.3)
        
        cv2.rectangle(frame, 
                     (margen_lados, margen_arriba),
                     (w - margen_lados, h - margen_abajo),
                     (0, 255, 255), 2)
        
        # Texto de guía
        cv2.putText(frame, "Area optima de captura", 
                   (margen_lados + 10, margen_arriba + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Línea central
        cv2.line(frame, (w//2, 0), (w//2, h), (255, 255, 0), 1)
        
        # Instrucciones
        cv2.putText(frame, f"Distancia optima: {self.DISTANCIA_OPTIMA}m",
                   (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Presiona CAPTURAR cuando este listo",
                   (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def calcular_visibilidad(self, landmarks):
        """Calcula la visibilidad promedio de los landmarks clave"""
        indices_clave = [0, 11, 12, 23, 24, 25, 26, 27, 28]  # Cabeza, hombros, caderas, piernas
        visibilidades = [landmarks.landmark[i].visibility for i in indices_clave]
        return np.mean(visibilidades)
    
    def capturar_foto(self):
        """Captura la foto actual y procesa con el modelo"""
        if self.current_frame is None:
            try:
                messagebox.showwarning("Advertencia", "No hay frame disponible")
            except Exception:
                # Si la UI fue destruida, evita que Tkinter lance TclError
                print("Advertencia: No hay frame disponible (messagebox no disponible)")
            return
        
        if self.modelo is None:
            try:
                messagebox.showerror("Error", "Modelo no cargado")
            except Exception:
                # Evitar crash si la ventana principal ya fue destruida
                print("Error: Modelo no cargado (messagebox no disponible)")
            return
        
        try:
            # Guardar imagen capturada
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captura_{timestamp}.jpg"
            filepath = os.path.join(self.directorio_capturas, filename)
            
            cv2.imwrite(filepath, self.current_frame)
            
            self.status_bar.config(
                text=f"Estado: Procesando imagen... 🔄",
                bg='#f39c12'
            )
            self.root.update()
            
            # Procesar en thread separado para no bloquear UI
            thread = threading.Thread(
                target=self.procesar_y_predecir,
                args=(filepath, timestamp)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al capturar: {e}")
            self.status_bar.config(
                text=f"Estado: Error en captura ❌",
                bg='#e74c3c'
            )
    
    def procesar_y_predecir(self, filepath, timestamp):
        """Procesa la imagen y predice la estatura"""
        try:
            # Cargar imagen
            image = cv2.imread(filepath)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detectar pose
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Advertencia",
                    "No se detectó una persona completa en la imagen.\n"
                    "Asegúrate de que la persona esté completamente visible."
                ))
                self.root.after(0, lambda: self.status_bar.config(
                    text="Estado: No se detectó persona ⚠️",
                    bg='#e67e22'
                ))
                return
            
            # Extraer características
            caracteristicas = self.extraer_caracteristicas(image, results.pose_landmarks)
            
            # Verificar visibilidad (característica #10: confidence_avg)
            visibility = caracteristicas[9]  # índice 9 = confidence_avg
            if visibility < 0.7:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Advertencia",
                    f"Calidad de detección baja (visibilidad: {visibility:.1%}).\n"
                    "Mejora la iluminación y asegúrate de que la persona esté completamente visible."
                ))
            
            # Preparar datos (USAR TODAS las 15 características)
            X = np.array(caracteristicas).reshape(1, -1)  # Todas las 15 características
            X_scaled = self.scaler.transform(X)
            
            # Predecir
            altura_pred = self.modelo.predict(X_scaled)[0]
            
            # Aplicar calibración si existe
            if self.calibracion:
                offset = self.calibracion['offset_aditivo']
                altura_pred += offset
                print(f"   🔧 Calibración aplicada: +{offset:.2f} cm")
            
            # Calcular confianza basada en visibilidad y características
            confianza = self.calcular_confianza(caracteristicas, visibility)
            
            # Crear imagen anotada
            imagen_anotada = self.crear_imagen_anotada(
                image, results.pose_landmarks, altura_pred, confianza
            )
            
            # Guardar imagen anotada
            output_filename = f"prediccion_{timestamp}.jpg"
            output_path = os.path.join(self.directorio_resultados, output_filename)
            cv2.imwrite(output_path, imagen_anotada)
            
            # Guardar JSON con resultados
            resultado = {
                'timestamp': timestamp,
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'imagen_original': filepath,
                'imagen_anotada': output_path,
                'altura_predicha_cm': round(altura_pred, 2),
                'confianza': round(confianza, 4),
                'visibilidad_landmarks': round(visibility, 4),
                'caracteristicas': {
                    'body_height_px': round(caracteristicas[0], 2),
                    'leg_length_px': round(caracteristicas[1], 2),
                    'torso_length_px': round(caracteristicas[2], 2),
                    'shoulder_width_px': round(caracteristicas[3], 2),
                    'hip_width_px': round(caracteristicas[4], 2),
                },
                'modelo_usado': self.metadata.get('model_name', 'N/A'),
                'mae_modelo': round(self.metadata.get('test_metrics', {}).get('mae', 0), 2)
            }
            
            json_path = os.path.join(self.directorio_resultados, f"prediccion_{timestamp}.json")
            with open(json_path, 'w') as f:
                json.dump(resultado, f, indent=2)
            
            # Guardar para mostrar
            self.ultima_prediccion = resultado
            
            # Actualizar UI en el thread principal
            self.root.after(0, lambda: self.mostrar_resultados(resultado))
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Estado: Predicción completada ✅ | Altura: {altura_pred:.1f} cm",
                bg='#27ae60'
            ))
            
            # Mostrar notificación
            self.root.after(0, lambda: messagebox.showinfo(
                "Predicción Completada",
                f"Altura predicha: {altura_pred:.1f} cm\n"
                f"Confianza: {confianza:.1%}\n\n"
                f"Imagen guardada en:\n{output_path}"
            ))
            
        except Exception as e:
            error_msg = f"Error al procesar: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Estado: Error en predicción ❌",
                bg='#e74c3c'
            ))
    
    def extraer_caracteristicas(self, image, landmarks):
        """Extrae características de la pose para el modelo (15 features)"""
        h, w = image.shape[:2]
        lm = landmarks.landmark
        
        # Extraer coordenadas clave
        nose = lm[0]
        left_shoulder = lm[11]
        right_shoulder = lm[12]
        left_hip = lm[23]
        right_hip = lm[24]
        left_knee = lm[25]
        right_knee = lm[26]
        left_ankle = lm[27]
        right_ankle = lm[28]
        
        # Calcular características básicas
        shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_mid_y = (left_hip.y + right_hip.y) / 2
        knee_mid_y = (left_knee.y + right_knee.y) / 2
        ankle_mid_y = (left_ankle.y + right_ankle.y) / 2
        
        body_height_px = (ankle_mid_y - nose.y) * h
        leg_length_px = (ankle_mid_y - hip_mid_y) * h
        torso_length_px = (hip_mid_y - shoulder_mid_y) * h
        shoulder_width_px = abs(right_shoulder.x - left_shoulder.x) * w
        
        # Características derivadas (DEBEN COINCIDIR con train_height_model.py)
        total_height_px = body_height_px * 1.02  # Ligeramente mayor con talones
        leg_to_torso_ratio = leg_length_px / (torso_length_px + 1e-6)
        height_to_width_ratio = body_height_px / (shoulder_width_px + 1e-6)
        
        # Visibilidades
        nose_visibility = nose.visibility
        ankle_visibility = (left_ankle.visibility + right_ankle.visibility) / 2
        confidence_avg = np.mean([lm[i].visibility for i in [0, 11, 12, 23, 24, 25, 26, 27, 28]])
        
        # Longitudes de muslo y pantorrilla
        thigh_length_px = (knee_mid_y - hip_mid_y) * h
        calf_length_px = (ankle_mid_y - knee_mid_y) * h
        
        # Dimensiones de imagen
        image_height = h
        image_width = w
        aspect_ratio = w / h
        
        # IMPORTANTE: Retornar exactamente 15 características en el mismo orden que el entrenamiento
        return [
            body_height_px,          # 1
            total_height_px,         # 2
            leg_length_px,           # 3
            torso_length_px,         # 4
            shoulder_width_px,       # 5
            leg_to_torso_ratio,      # 6
            height_to_width_ratio,   # 7
            nose_visibility,         # 8
            ankle_visibility,        # 9
            confidence_avg,          # 10
            thigh_length_px,         # 11
            calf_length_px,          # 12
            image_height,            # 13
            image_width,             # 14
            aspect_ratio             # 15
        ]
    
    def calcular_confianza(self, caracteristicas, visibility):
        """Calcula un índice de confianza para la predicción"""
        # Base: visibilidad
        confianza = visibility * 0.6
        
        # Bonificación por proporciones razonables
        leg_torso_ratio = caracteristicas[5]
        if 0.8 < leg_torso_ratio < 1.5:
            confianza += 0.2
        else:
            confianza += 0.1
        
        # Bonificación por altura corporal detectada razonable
        body_height_px = caracteristicas[0]
        if 300 < body_height_px < 1200:
            confianza += 0.2
        else:
            confianza += 0.1
        
        return min(confianza, 0.99)
    
    def crear_imagen_anotada(self, image, landmarks, altura_pred, confianza):
        """Crea imagen con anotaciones de predicción"""
        img_anotada = image.copy()
        h, w = img_anotada.shape[:2]
        
        # Dibujar landmarks
        for idx, landmark in enumerate(landmarks.landmark):
            if landmark.visibility > 0.5:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(img_anotada, (x, y), 5, (0, 255, 0), -1)
        
        # Dibujar líneas de conexión
        conexiones = [
            (11, 12), (11, 23), (12, 24), (23, 24),
            (23, 25), (24, 26), (25, 27), (26, 28)
        ]
        for start, end in conexiones:
            if (landmarks.landmark[start].visibility > 0.5 and 
                landmarks.landmark[end].visibility > 0.5):
                x1 = int(landmarks.landmark[start].x * w)
                y1 = int(landmarks.landmark[start].y * h)
                x2 = int(landmarks.landmark[end].x * w)
                y2 = int(landmarks.landmark[end].y * h)
                cv2.line(img_anotada, (x1, y1), (x2, y2), (255, 0, 0), 3)
        
        # Añadir texto con predicción
        cv2.rectangle(img_anotada, (10, 10), (w - 10, 150), (0, 0, 0), -1)
        cv2.rectangle(img_anotada, (10, 10), (w - 10, 150), (0, 255, 0), 3)
        
        cv2.putText(img_anotada, f"ALTURA PREDICHA: {altura_pred:.1f} cm",
                   (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(img_anotada, f"Confianza: {confianza:.1%}",
                   (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(img_anotada, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                   (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return img_anotada
    
    def mostrar_resultados(self, resultado):
        """Muestra los resultados en el panel derecho"""
        self.resultados_text.config(state='normal')
        self.resultados_text.delete('1.0', 'end')
        
        texto = f"""
╔══════════════════════════════════════════════╗
║         RESULTADO DE PREDICCIÓN              ║
╚══════════════════════════════════════════════╝

📏 ALTURA PREDICHA: {resultado['altura_predicha_cm']:.1f} cm

🎯 Confianza: {resultado['confianza']:.1%}
👁️  Visibilidad: {resultado['visibilidad_landmarks']:.1%}

📅 Fecha: {resultado['fecha']}

───────────────────────────────────────────────

📊 CARACTERÍSTICAS DETECTADAS:
───────────────────────────────────────────────
  • Altura corporal: {resultado['caracteristicas']['body_height_px']:.0f} px
  • Longitud piernas: {resultado['caracteristicas']['leg_length_px']:.0f} px
  • Longitud torso: {resultado['caracteristicas']['torso_length_px']:.0f} px
  • Ancho hombros: {resultado['caracteristicas']['shoulder_width_px']:.0f} px
  • Ancho caderas: {resultado['caracteristicas']['hip_width_px']:.0f} px

───────────────────────────────────────────────

🤖 INFORMACIÓN DEL MODELO:
───────────────────────────────────────────────
  • Modelo: {resultado['modelo_usado']}
  • Precisión: MAE = {resultado['mae_modelo']:.2f} cm
  • El 70% de las predicciones tienen
    error menor a 5 cm

───────────────────────────────────────────────

📁 ARCHIVOS GUARDADOS:
───────────────────────────────────────────────
  • Original: {os.path.basename(resultado['imagen_original'])}
  • Anotada: {os.path.basename(resultado['imagen_anotada'])}
  • JSON: prediccion_{resultado['timestamp']}.json

═══════════════════════════════════════════════
"""
        
        self.resultados_text.insert('1.0', texto)
        self.resultados_text.config(state='disabled')
    
    def cargar_imagen_externa(self):
        """Permite cargar una imagen externa para procesar"""
        if self.modelo is None:
            messagebox.showerror("Error", "Modelo no cargado")
            return
        
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if filepath:
            try:
                # Copiar a carpeta de capturas
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cargada_{timestamp}.jpg"
                dest_path = os.path.join(self.directorio_capturas, filename)
                
                import shutil
                shutil.copy(filepath, dest_path)
                
                self.status_bar.config(
                    text=f"Estado: Procesando imagen cargada... 🔄",
                    bg='#f39c12'
                )
                
                # Procesar
                thread = threading.Thread(
                    target=self.procesar_y_predecir,
                    args=(dest_path, timestamp)
                )
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar imagen: {e}")
    
    def abrir_carpeta_capturas(self):
        """Abre la carpeta de capturas en el explorador"""
        try:
            os.system(f'xdg-open "{self.directorio_capturas}"')
        except:
            messagebox.showinfo("Información", 
                              f"Carpeta de capturas:\n{os.path.abspath(self.directorio_capturas)}")
    
    def abrir_carpeta_resultados(self):
        """Abre la carpeta de resultados en el explorador"""
        try:
            os.system(f'xdg-open "{self.directorio_resultados}"')
        except:
            messagebox.showinfo("Información",
                              f"Carpeta de resultados:\n{os.path.abspath(self.directorio_resultados)}")
    
    def detener_camara(self):
        """Detiene la captura de cámara"""
        self.captura_activa = False
        if self.camera:
            self.camera.release()
        
        self.video_label.configure(
            image='',
            text="Cámara detenida\n\nPresiona 'Iniciar Cámara' para reanudar",
            fg='white',
            font=('Arial', 16)
        )
        
        self.btn_iniciar_camara.config(state='normal')
        self.btn_capturar.config(state='disabled')
        self.btn_detener.config(state='disabled')
        self.status_bar.config(
            text="Estado: Cámara detenida ⏸️",
            bg='#95a5a6'
        )
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación limpiamente"""
        if self.captura_activa:
            self.detener_camara()
        if self.pose:
            self.pose.close()
        self.root.destroy()


def main():
    """Función principal"""
    # Verificar que existe un modelo entrenado
    modelos = list(Path('.').glob('modelo_altura_*.pkl'))
    if not modelos:
        print("=" * 80)
        print("⚠️  ADVERTENCIA: No se encontró ningún modelo entrenado")
        print("=" * 80)
        print("\nPor favor, entrena el modelo primero ejecutando:")
        print("  python train_height_model.py")
        print("\nO usa el menú del sistema:")
        print("  ./menu_sistema.sh")
        print("=" * 80)
        
        respuesta = input("\n¿Deseas continuar de todos modos? (s/n): ")
        if respuesta.lower() != 's':
            return
    
    # Crear ventana principal
    root = tk.Tk()
    app = SistemaCapturaPrediccion(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
    
    # Iniciar aplicación
    print("=" * 80)
    print("🚀 Sistema de Captura y Predicción de Estatura iniciado")
    print("=" * 80)
    print("\n📸 Instrucciones:")
    print("  1. Haz clic en 'Iniciar Cámara'")
    print("  2. Coloca a la persona a 2.5 metros de distancia")
    print("  3. Asegúrate de que la persona esté completamente visible")
    print("  4. Haz clic en 'Capturar Foto' cuando esté lista")
    print("  5. Espera la predicción automática")
    print("\n💡 También puedes cargar imágenes externas usando 'Cargar Imagen'")
    print("=" * 80)
    
    root.mainloop()


if __name__ == "__main__":
    main()
