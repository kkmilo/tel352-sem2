from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from PIL import Image
import io
import cv2

# Import your function that wraps the big script
from sistema_altura.api_wrapper import run_height_prediction_from_image

# Import your body-measurements package
#from body_measurements_pkg import get_measurements


app = FastAPI()


@app.post("/predict/height")
async def predict_height(image: UploadFile = File(...)):
    img_bytes = await image.read()
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    res = run_height_prediction_from_image(pil_img)

    # Convert annotated image back to PNG bytes
    _, buffer = cv2.imencode(".png", res["annotated_image"])
    annotated_bytes = buffer.tobytes()

    return Response(
        content=annotated_bytes,
        media_type="image/png",
        headers={
            "X-Height-Predicted": str(res["altura_predicha_cm"]),
            "X-Height-Raw": str(res["altura_sin_calibracion_cm"]),
            "X-Confidence": str(res["confianza"]),
        }
    )


#@app.post("/predict/body")
#async def predict_body(image: UploadFile = File(...)):
#    img_bytes = await image.read()
#    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
#
#    measurements = get_measurements(pil_img)
#
#    return { "measurements": measurements }
