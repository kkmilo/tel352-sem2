from tkinter import *
import cv2
import math
from PIL import Image, ImageTk
import sys
from catalogo_prendas import catalogo_prendas


# Translation dictionary for measurements
traduccion_medidas = {
    "height": "altura",
    "waist": "cintura",
    "belly": "estomago",
    "chest": "pecho",
    "wrist": "muñeca",
    "neck": "cuello",
    "arm length": "largo_brazo",
    "thigh": "muslo",
    "shoulder width": "ancho_hombros",
    "hips": "cadera",
    "ankle": "tobillo"
}

# === Import your body measurement model ===
from ModuleBodyMeasurements.inference_function import run_inference #PC
# from ModuleBodyMeasurements.inference_function_tflite import run_inference #Raspi

# === Fonts ===
title_font = ("Times New Roman", 100, "bold")
subtitle_font = ("Times New Roman", 50)
normal_font = ("Times New Roman", 30)



# === Camera setup ===
cap = cv2.VideoCapture(0)
width, height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
after_id = None


def open_camera():
    """Continuously show webcam feed."""
    global after_id

    # Capture the video frame by frame
    _, frame = cap.read()

    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    video_label.photo_image = photo_image

    # Configure image in the label
    video_label.configure(image=photo_image)

    # Repeat the same process after every 10 seconds
    after_id = video_label.after(10, open_camera)


def show_temporary_message():
    """Temporarily show 'Analizando imagen...' message."""
    global after_id
    button2.place_forget()
    app.after_cancel(after_id)
    after_id = None
    video_label.place_forget()
    analisis.place(x=950, y=750)
    # Schedule the clear_message function to run after 3000 milliseconds (3 seconds)
    app.after(3000, clear_message)


def clear_message():
    analisis.place_forget()


def save_image():
    """Capture and save a photo from the camera."""
    _, frame = cap.read()
    cv2.imwrite("captured_image.jpg", frame)
    show_temporary_message()


def analizar_imagen():
    """Run body measurement inference and display recommendations."""
    save_image()  # take and save the snapshot

    try:
        height_label.place_forget()
        height_entry.place_forget()
        prenda_label.place_forget()
        prenda_menu.place_forget()
        button2.place_forget()


        analisis.place(x=950, y=750)
        app.update_idletasks()  # show "Analizando imagen..." before processing

        # Get height value
        height_cm = int(height_var.get())

        # Run the body measurement inference model
        # result = run_inference("captured_image.jpg", height_cm)
        result = run_inference("felipe1.jpg", height_cm)

        #traducir medidas
        result = {traduccion_medidas[k]: v for k, v in result.items() if k in traduccion_medidas}  

        # Hide 'analyzing' label once done
        analisis.place_forget()

        # Format model output
        if isinstance(result, dict):
            text = "\n".join(f"{k}: {v}" for k, v in result.items())
        else:
            text = str(result)

        # Automatically find best match for a chosen clothing type (example: "shirt")
        # You can change "shirt" to any other type existing in your catalogo_prendas
        match_result = match_prenda(result, prenda_var.get())

        # Combine both results
        full_text = f"{text}\n\n{match_result}"

        # Display results on screen
        result_text.place(x=10, y=400)
        result_text.config(text=full_text)


    except ValueError as e:
        analisis.place_forget()
        result_text.place(x=10, y=400)
        result_text.config(text="Por favor ingrese una altura válida (número).")
        print(f"[ERROR] {e}")

    except Exception as e:
        analisis.place_forget()
        result_text.place(x=10, y=400)
        result_text.config(text=f"Error al analizar la imagen:\n{e}")
        print(f"[ERROR] {e}")

    button3.place(x=250, y=750)

def match_prenda(model_results, prenda):
    # Filter catalog by type
    candidates = [c for c in catalogo_prendas if c["tipo"] == prenda]
    if not candidates:
        return "No hay prendas de ese tipo."

    best_match = None
    best_score = float("inf")

    for c in candidates:
        c_meas = c["medidas"]
        # Compare only keys both have
        common_keys = [k for k in c_meas.keys() if k in model_results]
        if not common_keys:
            continue
        # Compute Euclidean distance
        diff = math.sqrt(sum((model_results[k] - c_meas[k]) ** 2 for k in common_keys))
        if diff < best_score:
            best_score = diff
            best_match = c

    if best_match:
        return f"Recomendación: {best_match['nombre']} (diferencia promedio: {best_score:.1f})"
    else:
        return "No se encontró una coincidencia adecuada."
    

#def mostrar_ocultar_bienvenida():
#    """Toggle welcome screen and camera view."""
#    if button1.winfo_manager():
#        video_label.place(x=800, y=100)
#        button2.place(x=950, y=600)
#        open_camera()
#        button1.place_forget()
#        subtitle.place_forget()
#        height_label.place(x=550, y=650)
#        height_entry.place(x=750, y=650)
#    else:
#        button1.place(x=250, y=450)
#        subtitle.place(x=50, y=700)
#        button3.place_forget()
#        result_text.place_forget()

# === Toggle screens ===
def mostrar_ocultar_bienvenida():
    """Switch between welcome and camera mode."""
    if button1.winfo_ismapped():  # if INICIAR is visible → go to camera
        button1.place_forget()
        subtitle.place_forget()

        video_label.place(x=900, y=200)
        button2.place(x=1000, y=800)
        height_label.place(x=700, y=700)
        height_entry.place(x=880, y=700)
        prenda_label.place(x=700, y=770)
        prenda_menu.place(x=880, y=770)

        open_camera()
    else:
        # Return to welcome screen
        for widget in [video_label, analisis, result_text, button2, button3,
                       height_label, height_entry, prenda_label, prenda_menu]:
            widget.place_forget()
        titulo.place(x=50, y=30)
        subtitle.place(x=50, y=700)
        button1.place(x=250, y=450)




# === Tkinter UI Setup ===
app = Tk()
app.title("Giorgio IArmani")
app.state('zoomed')
app.bind('<Escape>', lambda e: app.quit())

# === Load background ===
original_bg = Image.open("./background.jpg")
bg_image = ImageTk.PhotoImage(original_bg)
fondo = Label(app, image=bg_image)
fondo.place(x=0, y=0, relwidth=1, relheight=1)

video_label = Label(app, bg="white")

# === Fonts ===
title_font = ("Times New Roman", 60, "bold")
subtitle_font = ("Times New Roman", 30, "italic")
normal_font = ("Times New Roman", 25)
result_font = ("Times New Roman", 20)

# === Text and labels ===
titulo = Label(app, text="Giorgio\nIArmani", font=title_font, fg="black", bg="white")
subtitle = Label(app, text="Asistente de Compras de Vestuario", font=subtitle_font, fg="black", bg="white")
analisis = Label(app, text="Analizando imagen...", font=normal_font, fg="black", bg="white")
result_text = Label(app, text="", font=result_font, fg="black", bg="white", justify=LEFT, wraplength=800)

# === Buttons ===
button1 = Button(app, text="INICIAR", font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=lambda: mostrar_ocultar_bienvenida())
button2 = Button(app, text="Tomar foto", font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=analizar_imagen)
button3 = Button(app, text="Finalizar", font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=mostrar_ocultar_bienvenida)

# === Inputs ===
height_label = Label(app, text="Altura (cm):", font=normal_font, fg="black", bg="white")
height_var = StringVar(value="170")
height_entry = Entry(app, textvariable=height_var, font=normal_font, width=5)

prenda_var = StringVar(value="camisa")
prenda_label = Label(app, text="Tipo de prenda:", font=normal_font, bg="white")
prenda_menu = OptionMenu(app, prenda_var, "camisa", "pantalón", "chaqueta", "polera")

# === Show only welcome screen initially ===
titulo.place(x=50, y=30)
subtitle.place(x=50, y=700)
button1.place(x=250, y=450)

# Everything else hidden
for widget in [video_label, analisis, result_text, button2, button3,
               height_label, height_entry, prenda_label, prenda_menu]:
    widget.place_forget()

def resize_ui(event=None):
    w, h = app.winfo_width(), app.winfo_height()
    # Resize background
    resized_bg = original_bg.resize((w, h))
    bg_photo = ImageTk.PhotoImage(resized_bg)
    fondo.config(image=bg_photo)
    fondo.image = bg_photo  # prevent garbage collection

    # Only place/move widgets if they are currently visible
    if titulo.winfo_ismapped():
        titulo.place(x=w * 0.03, y=h * 0.03)
    if subtitle.winfo_ismapped():
        subtitle.place(x=w * 0.03, y=h * 0.80)
    if button1.winfo_ismapped():
        button1.place_configure(x=w * 0.25, y=h * 0.45)
    if video_label.winfo_ismapped():
        video_label.place_configure(x=w * 0.55, y=h * 0.15)
    if button2.winfo_ismapped():
        button2.place_configure(x=w * 0.60, y=h * 0.75)
    if button3.winfo_ismapped():
        button3.place_configure(x=w * 0.15, y=h * 0.80)
    if result_text.winfo_ismapped():
        result_text.place_configure(x=w * 0.05, y=h * 0.40)
    if height_label.winfo_ismapped():
        height_label.place_configure(x=w * 0.35, y=h * 0.70)
    if height_entry.winfo_ismapped():
        height_entry.place_configure(x=w * 0.47, y=h * 0.70)
    if prenda_label.winfo_ismapped():
        prenda_label.place_configure(x=w * 0.35, y=h * 0.77)
    if prenda_menu.winfo_ismapped():
        prenda_menu.place_configure(x=w * 0.47, y=h * 0.77)
    if analisis.winfo_ismapped():
        analisis.place_configure(x=w * 0.60, y=h * 0.85)



# === After analysis ===
def mostrar_resultado(resultado_texto):
    """Display results and finalize button."""
    analisis.place_forget()
    result_text.config(text=resultado_texto)
    result_text.place(x=100, y=500)
    button3.place(x=250, y=850)

app.bind("<Configure>", resize_ui)
app.mainloop()
