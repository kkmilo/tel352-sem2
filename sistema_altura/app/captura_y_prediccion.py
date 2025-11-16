#!/usr/bin/env python3

import cv2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
import joblib  # Para cargar scaler (StandardScaler)

# Importar intérprete TFLite
try:
    from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter
except ImportError:
    try:
        import tensorflow as tf  # type: ignore
        TFLiteInterpreter = tf.lite.Interpreter  # type: ignore[attr-defined]
    except Exception as _e:
        raise RuntimeError(
            "TensorFlow Lite no está instalado o no es compatible con esta versión de Python. "
            "Instala 'tflite-runtime' (si usas Python <3.12) o 'tensorflow' (si usas Python >=3.12)."
        ) from _e
import json
import os
from datetime import datetime
import time
import threading
from pathlib import Path

# Patrón de archivo para modelos TFLite
MODEL_PATTERN_TFLITE = 'modelo_altura_*.tflite'


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
        self.modelo = None  # No se usa (TFLite solamente)
        self.scaler = None
        self.metadata = None
        self.calibracion = None  # Calibración con datos reales
        self.mp_pose = mp.solutions.pose
        self.pose = None
        self.ultima_prediccion = None
        self.modelo_dir = None  # Directorio del modelo cargado
        self.modelo_timestamp = None  # Timestamp del modelo cargado
        
        # Intérprete TFLite
        self.tflite_interpreter = None
        self.tflite_input_details = None
        self.tflite_output_details = None
        
        # Auto-captura
        self.auto_captura_habilitada = True
        self.auto_cuenta_regresiva_seg = 3
        self._auto_en_countdown = False
        self._auto_t_inicio = 0.0
        self._auto_ultima_captura = 0.0
        self._auto_cooldown_seg = 2.0
        
        # Configuración
        self.DISTANCIA_OPTIMA = 2.1  # metros
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
        # Auto-inicio de cámara tras inicializar pose
        try:
            self.iniciar_camara()
        except Exception as _e:
            print(f"⚠️  No se pudo iniciar la cámara automáticamente: {_e}")
        
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
        
        # Auto-captura: toggle
        auto_frame = tk.Frame(left_frame, bg='#34495e')
        auto_frame.pack(fill='x', padx=10, pady=5)
        
        self.var_auto = tk.BooleanVar(value=self.auto_captura_habilitada)
        tk.Checkbutton(
            auto_frame,
            text="Auto-captura (3s)",
            variable=self.var_auto,
            onvalue=True,
            offvalue=False,
            command=self._toggle_auto_captura,
            bg='#34495e',
            fg='white',
            selectcolor='#2c3e50',
            activebackground='#34495e',
            activeforeground='white'
        ).pack(anchor='w')
        
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
        
        modelo_cargado = (self.tflite_interpreter is not None)
        modelo_color = '#27ae60' if modelo_cargado else '#e74c3c'
        modelo_texto = '✅ Modelo TFLite cargado' if modelo_cargado else '❌ Modelo no encontrado'
        
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

        # Botón de calibración del modelo
        tk.Button(
            modelo_frame,
            text="🛠️ Calibrar (ingresar altura real)",
            command=self.calibrar_con_altura,
            font=('Arial', 10, 'bold'),
            bg='#2ecc71',
            fg='white',
            relief='raised',
            bd=2,
            padx=10,
            pady=6,
            cursor='hand2'
        ).pack(fill='x', padx=10, pady=6)
        
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
✅ Distancia: 2.0m - 2.5m (ideal 2.1m)
✅ Cámara estable (trípode recomendado)
✅ Altura de cámara: 1.2-1.3m del suelo
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
        modelo_cargado = (self.tflite_interpreter is not None)
        self.status_bar = tk.Label(
            self.root,
            text="Estado: Listo | Modelo cargado ✅" if modelo_cargado else "Estado: Modelo no encontrado ❌",
            font=('Arial', 10),
            bg='#1abc9c' if modelo_cargado else '#e74c3c',
            fg='white',
            anchor='w',
            relief='sunken',
            bd=1,
            padx=10,
            pady=5
        )
        self.status_bar.pack(side='bottom', fill='x')
        
    def cargar_modelo_automatico(self):
        """Carga automáticamente el modelo TFLite más reciente"""
        try:
            # Buscar archivos de modelo en el directorio 'app' y en la carpeta 'modelos' del proyecto
            import os
            app_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'

            modelos = list(Path(app_dir).glob(MODEL_PATTERN_TFLITE))

            # Si no hay modelos en app/, buscar en ../modelos (raíz del proyecto)
            if not modelos:
                project_root = Path(app_dir).parent
                modelos_dir = project_root / 'modelos'
                print(f"ℹ️  No se encontraron modelos en {app_dir}. Buscando en {modelos_dir}...")
                if modelos_dir.exists():
                    modelos = list(modelos_dir.glob(MODEL_PATTERN_TFLITE))

            if not modelos:
                print("⚠️ No se encontraron modelos TFLite entrenados")
                print(f"   Buscando en: {app_dir}")
                print(f"   También se buscó en: {str(project_root / 'modelos')}")
                print("   Por favor, entrena el modelo primero con: python scripts/entrenar_dnn_altura.py")
                return False

            # Usar el más reciente
            modelo_path = max(modelos, key=lambda p: p.stat().st_mtime)

            print(f"📂 Cargando modelo: {modelo_path.name}")

            # Extraer timestamp (últimas 2 partes: fecha_hora)
            parts = modelo_path.stem.split('_')
            timestamp = '_'.join(parts[-2:])
            # Guardar referencia del modelo actual
            self.modelo_dir = Path(modelo_path).parent
            self.modelo_timestamp = timestamp

            # Cargar modelo TFLite
            self.tflite_interpreter = TFLiteInterpreter(model_path=str(modelo_path))
            self.tflite_interpreter.allocate_tensors()
            self.tflite_input_details = self.tflite_interpreter.get_input_details()
            self.tflite_output_details = self.tflite_interpreter.get_output_details()
            
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
                print("   ℹ️  Sin calibración (usa 'python calibrar_modelo.py' para mejorar precisión)")

            print("✅ Modelo TFLite cargado exitosamente")
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

                    # Auto-captura: condición de distancia excelente + visibilidad alta
                    condicion_ok = self._evaluar_distancia_excelente(frame, results.pose_landmarks) and visibility > 0.9
                    ahora = time.time()
                    # Respetar cooldown tras una captura
                    en_cooldown = (ahora - self._auto_ultima_captura) < self._auto_cooldown_seg
                    
                    if self.auto_captura_habilitada and not en_cooldown:
                        if condicion_ok:
                            if not self._auto_en_countdown:
                                self._auto_en_countdown = True
                                self._auto_t_inicio = ahora
                                try:
                                    self.status_bar.config(text="Estado: Distancia EXCELENTE - Captura en 3s ⏳", bg='#27ae60')
                                except Exception:
                                    pass
                            # Mostrar cuenta regresiva
                            restante = int(self.auto_cuenta_regresiva_seg - (ahora - self._auto_t_inicio)) + 1
                            if restante > 0:
                                self._dibujar_countdown(frame, restante)
                            else:
                                self._auto_en_countdown = False
                                self._auto_ultima_captura = ahora
                                self.capturar_foto()
                        else:
                            # Cancelar countdown si se pierde la condición
                            self._auto_en_countdown = False
                    else:
                        # Si no está habilitada o está en cooldown, cancelar countdown
                        self._auto_en_countdown = False
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

    def _evaluar_distancia_excelente(self, frame, landmarks):
        """Evalúa si la persona ocupa entre 70% y 90% de la altura del encuadre
        y está centrada horizontalmente (aprox), como proxy de 'distancia excelente'."""
        h = frame.shape[0]
        lm = landmarks.landmark
        nose = lm[0]
        ankle_mid_y = (lm[27].y + lm[28].y) / 2
        body_height_px = (ankle_mid_y - nose.y) * h
        ratio_altura = body_height_px / max(h, 1)
        
        # centrado horizontal aproximado usando hombros
        left_shoulder = lm[11]
        right_shoulder = lm[12]
        mid_x = (left_shoulder.x + right_shoulder.x) / 2
        # márgenes laterales (30% como en la guía dibujada)
        margen_lados = 0.3
        centrado_ok = (margen_lados < mid_x < 1.0 - margen_lados)
        
        return (0.70 <= ratio_altura <= 0.90) and centrado_ok

    def _dibujar_countdown(self, frame, restante):
        """Dibuja overlay con la cuenta regresiva."""
        h, w = frame.shape[:2]
        texto = str(max(1, restante))
        (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 4, 8)
        x = (w - tw) // 2
        y = (h + th) // 2
        cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 8)

    def _toggle_auto_captura(self):
        self.auto_captura_habilitada = bool(self.var_auto.get())
    
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
        instruccion = (
            "Captura automatica en 3s"
            if self.auto_captura_habilitada else
            "Presiona CAPTURAR cuando esté listo"
        )
        cv2.putText(frame, instruccion,
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
        
        # Verificar que el intérprete TFLite y el scaler estén disponibles
        if self.tflite_interpreter is None or self.scaler is None:
            try:
                messagebox.showerror("Error", "Modelo no cargado. Asegúrate de que el .tflite y el scaler estén disponibles.")
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
                text="Estado: Procesando imagen... 🔄",
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
                text="Estado: Error en captura ❌",
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
            # Importante: el orden de características debe coincidir con metadata/entrenamiento
            visibility = caracteristicas[9]  # índice 9 = confidence_avg
            if visibility < 0.7:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Advertencia",
                    f"Calidad de detección baja (visibilidad: {visibility:.1%}).\n"
                    "Mejora la iluminación y asegúrate de que la persona esté completamente visible."
                ))
            
            # Preparar datos (USAR TODAS las 15 características)
            X = np.array(caracteristicas, dtype=np.float32).reshape(1, -1)  # Todas las 15 características
            x_scaled = self.scaler.transform(X)

            # Predecir con TFLite
            input_idx = self.tflite_input_details[0]['index']
            # Asegurar dtype y shape esperados por el modelo
            inp = x_scaled.astype(self.tflite_input_details[0]['dtype'])
            self.tflite_interpreter.set_tensor(input_idx, inp)
            self.tflite_interpreter.invoke()
            output_idx = self.tflite_output_details[0]['index']
            out = self.tflite_interpreter.get_tensor(output_idx)
            altura_pred_raw = float(out.reshape(-1)[0])
            altura_pred = altura_pred_raw
            
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
                'altura_sin_calibracion_cm': round(altura_pred_raw, 2),
                'confianza': round(confianza, 4),
                'visibilidad_landmarks': round(visibility, 4),
                'caracteristicas': {
                    # Mapeo corregido de índices a nombres (según metadata)
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
                text="Estado: Error en predicción ❌",
                bg='#e74c3c'
            ))
    
    def extraer_caracteristicas(self, image, landmarks):
        """Extrae características de la pose para el modelo (15 features)
        El ORDEN debe coincidir con `feature_names` en el metadata del modelo TFLite.
        Orden esperado:
        [
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
        """
        h, w = image.shape[:2]
        lm = landmarks.landmark
        
        # Extraer coordenadas clave
        nose = lm[0]
        left_shoulder = lm[11]
        right_shoulder = lm[12]
        left_hip = lm[23]
        right_hip = lm[24]
    # Rodillas no utilizadas en el conjunto de características actual
        left_ankle = lm[27]
        right_ankle = lm[28]
        
        # Calcular características básicas
        shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_mid_y = (left_hip.y + right_hip.y) / 2
        ankle_mid_y = (left_ankle.y + right_ankle.y) / 2
        
        body_height_px = (ankle_mid_y - nose.y) * h
        leg_length_px = (ankle_mid_y - hip_mid_y) * h
        torso_length_px = (hip_mid_y - shoulder_mid_y) * h
        shoulder_width_px = abs(right_shoulder.x - left_shoulder.x) * w
        hip_width_px = abs(right_hip.x - left_hip.x) * w
        
        # Características derivadas (DEBEN COINCIDIR con el entrenamiento)
        leg_to_torso_ratio = leg_length_px / (torso_length_px + 1e-6)
        height_to_width_ratio = body_height_px / (shoulder_width_px + 1e-6)
        
        # Visibilidades
        nose_visibility = nose.visibility
        left_shoulder_visibility = left_shoulder.visibility
        right_shoulder_visibility = right_shoulder.visibility
        left_hip_visibility = left_hip.visibility
        right_hip_visibility = right_hip.visibility
        confidence_avg = np.mean([
            lm[i].visibility for i in [0, 11, 12, 23, 24, 25, 26, 27, 28]
        ])

        # Dimensiones de imagen
        image_width = w
        image_height = h

        # IMPORTANTE: Retornar exactamente 15 características en el mismo orden que el entrenamiento
        return [
            body_height_px,            # 1: body_height_px
            leg_length_px,             # 2: leg_length_px
            torso_length_px,           # 3: torso_length_px
            shoulder_width_px,         # 4: shoulder_width_px
            hip_width_px,              # 5: hip_width_px
            leg_to_torso_ratio,        # 6: leg_to_torso_ratio
            height_to_width_ratio,     # 7: height_to_width_ratio
            image_width,               # 8: image_width
            image_height,              # 9: image_height
            confidence_avg,            # 10: confidence_avg
            nose_visibility,           # 11: nose_visibility
            left_shoulder_visibility,  # 12: left_shoulder_visibility
            right_shoulder_visibility, # 13: right_shoulder_visibility
            left_hip_visibility,       # 14: left_hip_visibility
            right_hip_visibility       # 15: right_hip_visibility
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

    def calibrar_con_altura(self):
        """Pide la altura real en cm y guarda un offset de calibración para futuras predicciones."""
        if self.ultima_prediccion is None:
            messagebox.showinfo(
                "Calibración",
                "Primero realiza una predicción (captura) y luego vuelve a intentar la calibración."
            )
            return

        altura_real = simpledialog.askfloat(
            "Calibración",
            "Ingresa tu altura real en centímetros:",
            minvalue=120.0,
            maxvalue=220.0
        )
        if altura_real is None:
            return

        # Preferir predicción base sin calibración si está disponible
        altura_base = float(self.ultima_prediccion.get('altura_sin_calibracion_cm',
                                   self.ultima_prediccion.get('altura_predicha_cm', 0.0)))
        offset = float(altura_real - altura_base)

        # Persistir calibración y aplicarla en memoria
        self._guardar_calibracion(offset)
        self.calibracion = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'offset_aditivo': offset,
            'altura_real_cm': altura_real,
            'altura_sin_calibracion_cm': altura_base,
            'origen': 'usuario'
        }

        self.status_bar.config(
            text=f"Estado: Calibración aplicada ({offset:+.2f} cm)",
            bg='#1abc9c'
        )
        messagebox.showinfo(
            "Calibración aplicada",
            f"Offset guardado: {offset:+.2f} cm.\nLas próximas predicciones lo usarán automáticamente."
        )

    def _guardar_calibracion(self, offset: float):
        """Guarda calibracion_{timestamp}.json junto al modelo cargado."""
        base_dir = Path(self.modelo_dir) if self.modelo_dir else Path('modelos')
        base_dir.mkdir(parents=True, exist_ok=True)
        ts = self.modelo_timestamp or datetime.now().strftime('%Y%m%d_%H%M%S')
        path = base_dir / f"calibracion_{ts}.json"
        data = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'offset_aditivo': float(offset)
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def mostrar_resultados(self, resultado):
        """Muestra los resultados en el panel derecho"""
        self.resultados_text.config(state='normal')
        self.resultados_text.delete('1.0', 'end')
        
        texto = f"""
╔══════════════════════════════════════════════╗
║         RESULTADO DE PREDICCIÓN              ║
╚══════════════════════════════════════════════╝

📏 ALTURA PREDICHA (calibrada): {resultado['altura_predicha_cm']:.1f} cm
📐 Altura sin calibración: {resultado.get('altura_sin_calibracion_cm', 0):.1f} cm

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
        # Validar que el intérprete TFLite y el scaler estén cargados
        if self.tflite_interpreter is None or self.scaler is None:
            messagebox.showerror("Error", "Modelo no cargado. Asegúrate de que el .tflite, scaler y metadata estén disponibles.")
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
                    text="Estado: Procesando imagen cargada... 🔄",
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
        except Exception:
            messagebox.showinfo("Información", f"Carpeta de capturas:\n{os.path.abspath(self.directorio_capturas)}")
    
    def abrir_carpeta_resultados(self):
        """Abre la carpeta de resultados en el explorador"""
        try:
            os.system(f'xdg-open "{self.directorio_resultados}"')
        except Exception:
            messagebox.showinfo("Información", f"Carpeta de resultados:\n{os.path.abspath(self.directorio_resultados)}")
    
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
    # Verificar que existe un modelo TFLite entrenado (en app/ o en ../modelos)
    app_dir = Path(__file__).parent if '__file__' in globals() else Path('.')
    modelos_tflite = list(app_dir.glob('modelo_altura_*.tflite'))
    if not modelos_tflite:
        modelos_dir = app_dir.parent / 'modelos'
        if modelos_dir.exists():
            modelos_tflite = list(modelos_dir.glob('modelo_altura_*.tflite'))
    if not modelos_tflite:
        print("=" * 80)
        print("⚠️  ADVERTENCIA: No se encontró ningún modelo TFLite entrenado")
        print("=" * 80)
        print("\nPor favor, entrena el modelo primero ejecutando:")
        print("  python scripts/entrenar_dnn_altura.py")
        print("\nO usa el menú del sistema:")
        print("  ./menu_sistema.sh")
        print("=" * 80)
        # Continuar de todos modos; la app intentará cargar automáticamente si luego aparecen archivos
    
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
    print("  1. La cámara se inicia automáticamente")
    print("  2. Coloca a la persona a 2.5 metros de distancia")
    print("  3. Asegúrate de que la persona esté completamente visible")
    print("  4. Puedes capturar manualmente o esperar la auto-captura (3s en distancia EXCELENTE)")
    print("  5. Usa 'Calibrar' para ajustar con tu altura real si lo deseas")
    print("\n💡 También puedes cargar imágenes externas usando 'Cargar Imagen'")
    print("=" * 80)
    
    root.mainloop()


if __name__ == "__main__":
    main()
