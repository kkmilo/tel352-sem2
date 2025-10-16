from tkinter import *
import cv2
from PIL import Image, ImageTk
import sys

# === Import your body measurement model ===
from ModuleBodyMeasurements.inference_function import run_inference # make sure inference.py has run_inference()

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
        analisis.place(x=950, y=750)
        app.update_idletasks()  # show "Analizando imagen..." before processing

        # Get height value
        height_cm = int(height_var.get())

        # Cambiar a "captured_image.jpg" si se quiere usar la cámara
        result = run_inference("felipe1.jpg", height_cm)

        # Hide 'analyzing' label once done
        analisis.place_forget()


        # Format result depending on type
        if isinstance(result, dict):
            text = "\n".join(f"{k}: {v}" for k, v in result.items())
        else:
            text = str(result)

        result_text.place(x=10, y=400)
        result_text.config(text=text)

    except ValueError:
        analisis.place_forget()
        result_text.place(x=10, y=400)
        result_text.config(text="Por favor ingrese una altura válida (número).")

    except Exception as e:
        analisis.place_forget()
        result_text.place(x=10, y=400)
        result_text.config(text=f"Error al analizar la imagen:\n{e}")
        print(f"[ERROR] {e}")

    button3.place(x=250, y=750)


def mostrar_ocultar_bienvenida():
    """Toggle welcome screen and camera view."""
    if button1.winfo_manager():
        video_label.place(x=800, y=100)
        button2.place(x=950, y=600)
        open_camera()
        button1.place_forget()
        subtitle.place_forget()
        height_label.place(x=550, y=650)
        height_entry.place(x=750, y=650)
    else:
        button1.place(x=250, y=450)
        subtitle.place(x=50, y=700)
        button3.place_forget()
        result_text.place_forget()


# === Tkinter UI Setup ===
app = Tk()
app.title("Giorgio IArmani")
app.geometry("1600x900")
app.bind('<Escape>', lambda e: app.quit())

# === Background ===
img_pil = Image.open("./BG.jpg")
image = ImageTk.PhotoImage(img_pil)
fondo = Label(app, image=image)
fondo.place(x=0, y=0, relwidth=1, relheight=1)

video_label = Label(app)

# === Text and labels ===
titulo = Label(app, text="Giorgio\nIArmani", font=title_font, fg="black", bg="white")
titulo.place(x=50, y=30)

subtitle = Label(app, text="Asistente de Compras de Vestuario", font=subtitle_font, fg="black", bg="white")
subtitle.place(x=50, y=700)

analisis = Label(app, text="Analizando imagen...", font=normal_font, fg="black", bg="white")

result_text = Label(app, text="", font=subtitle_font, fg="black", bg="white")

# === Buttons ===
button1 = Button(app, text=("INICIAR"), font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=mostrar_ocultar_bienvenida)
button1.place(x=250, y=450)

button2 = Button(app, text=("Tomar foto"), font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=analizar_imagen)

button3 = Button(app, text=("Finalizar"), font=("Times New Roman", 50, "bold"),
                 fg="white", bg="#b75e66", command=mostrar_ocultar_bienvenida)

# === Height input ===
height_label = Label(app, text="Altura (cm):", font=normal_font, fg="black", bg="white")
#height_label.place(x=950, y=500)

height_var = StringVar(value="170")  # default
height_entry = Entry(app, textvariable=height_var, font=normal_font, width=5)
#height_entry.place(x=1150, y=500)

# === Run app ===
app.mainloop()
