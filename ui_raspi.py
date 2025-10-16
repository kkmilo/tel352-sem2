from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2

title_font = ("Times New Roman", 100, "bold")

subtitle_font = ("Times New Roman", 50)

normal_font = ("Times New Roman", 30)

picam2 = Picamera2()

width = 640
height = 480

config = picam2.create_preview_configuration(main={"size": (width, height)})
picam2.configure(config)

after_id = None

def open_camera():
    global after_id
    
    frame = picam2.capture_array()    
    
    try:
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    except cv2.error:
        # Si da error de color (o colores incorrectos), intenta la conversión RGB a RGBA
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)

    # Convertir el array numpy (opencv_image) a un objeto Image de PIL
    captured_image = Image.fromarray(opencv_image)

    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Actualizar el Label
    video_label.photo_image = photo_image
    video_label.configure(image=photo_image)

    # Repetir el proceso
    after_id = video_label.after(10, open_camera)

def show_temporary_message():
    global after_id

    button2.place_forget()  # Hide the button
    app.after_cancel(after_id)  # Stop updating the video feed
    after_id = None
    video_label.place_forget()  # Hide the video feed


    analisis.place(x=950, y=750)
    # Schedule the clear_message function to run after 3000 milliseconds (3 seconds)
    app.after(3000, clear_message)

def clear_message():
    analisis.place_forget()

def save_image():
    picam2.capture_file("captured_image.jpg")
    show_temporary_message()

def analizar_imagen():
    save_image()

    result = {"Prenda": "Camisa guayabera", "Color": "Azul", "Talla": "M"}
    result_text.place(x=10, y=400)
    result_text.config(text=f"Prenda: {result['Prenda']}\nColor: {result['Color']}\nTalla: {result['Talla']}")

    button3.place(x=250, y=750)

def mostrar_ocultar_bienvenida():
    global after_id
    
    if button1.winfo_manager():
        video_label.place(x=800, y=100)
        button2.place(x=950, y=600)
        picam2.start()
        open_camera()
        button1.place_forget()  # Ocultar el botón
        subtitle.place_forget()  # Ocultar el subtítulo
    else:
        if after_id is not None:
            app.after_cancel(after_id)
            after_id = None # Reinicia la variable
            
        picam2.stop()
        
        button1.place(x=250, y=450)  # Mostrar el botón en la posición original
        subtitle.place(x=50, y=700)  # Mostrar el subtítulo en la posición original
        button3.place_forget()  # Ocultar el botón de tomar foto
        result_text.place_forget()  # Ocultar el texto de resultado

app = Tk()
app.title("Giorgio IArmani")
app.geometry("1280x720")
app.bind('<Escape>', lambda e: app.quit())

img_pil = Image.open("/home/raspi/Desktop/background.jpg")
image = ImageTk.PhotoImage(img_pil)
fondo = Label(app, image=image)
fondo.place(x=0, y=0, relwidth=1, relheight=1)

video_label = Label(app)

titulo = Label(app, text="Giorgio\nIArmani", font=title_font, fg="black", bg="white")
titulo.place(x=50, y=30)

subtitle = Label(app, text="Asistente de Compras de Vestuario", font=subtitle_font, fg="black", bg="white")
subtitle.place(x=50, y=700)

analisis = Label(app, text="Analizando imagen...", font=normal_font, fg="black", bg="white")

result_text = Label(app, text="", font=subtitle_font, fg="black", bg="white")

button3 = Button(app, text=("Finalizar"), font=("Times New Roman", 50, "bold"), fg="white", bg="#b75e66", command=mostrar_ocultar_bienvenida)

button2 =  Button(app, text=("Tomar foto"), font=("Times New Roman", 50,"bold"), fg="white", bg="#b75e66", command=analizar_imagen)

button1 = Button(app, text=("INICIAR"), font=("Times New Roman", 50, "bold"), fg="white", bg="#b75e66", command=mostrar_ocultar_bienvenida)
button1.place(x=250, y=450)

app.mainloop()
