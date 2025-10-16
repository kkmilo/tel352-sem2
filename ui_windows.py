from tkinter import *
import cv2
from PIL import Image, ImageTk

title_font = ("Times New Roman", 100, "bold")

subtitle_font = ("Times New Roman", 50)

normal_font = ("Times New Roman", 30)

cap = cv2.VideoCapture(0)
width = 640
height = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
after_id = None

def open_camera():
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
    _, frame = cap.read()
    cv2.imwrite("captured_image.jpg", frame)
    show_temporary_message()

def analizar_imagen():
    save_image()

    result = {"Prenda": "Camisa guayabera", "Color": "Azul", "Talla": "M"}
    result_text.place(x=10, y=400)
    result_text.config(text=f"Prenda: {result['Prenda']}\nColor: {result['Color']}\nTalla: {result['Talla']}")

    button3.place(x=250, y=750)

def mostrar_ocultar_bienvenida():
    if button1.winfo_manager():
        video_label.place(x=800, y=100)
        button2.place(x=950, y=600)
        open_camera()
        button1.place_forget()  # Ocultar el botón
        subtitle.place_forget()  # Ocultar el subtítulo
    else:
        button1.place(x=250, y=450)  # Mostrar el botón en la posición original
        subtitle.place(x=50, y=700)  # Mostrar el subtítulo en la posición original
        button3.place_forget()  # Ocultar el botón de tomar foto
        result_text.place_forget()  # Ocultar el texto de resultado

app = Tk()
app.title("Giorgio IArmani")
app.geometry("1600x900")
app.bind('<Escape>', lambda e: app.quit())

img_pil = Image.open("C:/Users/desk/OneDrive - Universidad Técnica Federico Santa María/TEL3 Sem2/background.jpg")
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
