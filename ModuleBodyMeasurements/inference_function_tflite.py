import os
import numpy as np
import cv2
from PIL import Image
import tflite_runtime.interpreter as tflite
from ModuleBodyMeasurements.demo import main  # your measurement logic

# --------------------
# 🔹 Global interpreter instance
# --------------------
INTERPRETER_INSTANCE = None

# --------------------
# 🔹 TFLite Model Class
# --------------------
class DeepLabTFLiteModel:
    INPUT_SIZE = 513  # MobileNetV2 DeepLab default input

    def __init__(self, model_path: str):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        print("✅ TFLite model loaded successfully!")

    def run(self, image: Image.Image):
        """Run segmentation on input image and return resized image + mask."""

        resized_image = image.convert("RGB").resize((self.INPUT_SIZE, self.INPUT_SIZE), Image.ANTIALIAS)
        # Prepare input data depending on model type
        input_details = self.input_details[0]
        input_shape = input_details['shape']
        input_dtype = input_details['dtype']

        # Resize to model expected shape
        input_data = np.expand_dims(np.asarray(resized_image), axis=0)

        if input_dtype == np.uint8:
            # Quantized model: uint8 input
            input_data = input_data.astype(np.uint8)
        else:
            # Float model: normalize to [0,1] float32
            input_data = input_data.astype(np.float32) / 255.0

        # Set the tensor
        self.interpreter.set_tensor(input_details['index'], input_data)

        # Run inference
        self.interpreter.invoke()

        seg_map = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        return resized_image, seg_map


# --------------------
# 🔹 Inference Entrypoint
# --------------------
def run_inference(image_path: str, height: int):
    global INTERPRETER_INSTANCE

    # Path to your TFLite model
    MODEL_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "deeplab_model",
        "deeplab_mnv2.tflite"
    )

    if INTERPRETER_INSTANCE is None:
        INTERPRETER_INSTANCE = DeepLabTFLiteModel(MODEL_PATH)

    # Load image
    image_abs_path = os.path.join(os.getcwd(), image_path) if not os.path.isabs(image_path) else image_path
    image = Image.open(image_abs_path)

    # Run segmentation
    resized_image, seg = INTERPRETER_INSTANCE.run(image)

    # Resize segmentation mask to original image size
    seg = cv2.resize(seg.astype(np.uint8), image.size)
    mask_sel = (seg == 15).astype(np.float32)  # Pascal VOC 'person' class
    mask = 255 * mask_sel.astype(np.uint8)

    # Apply mask to image
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    res = cv2.bitwise_and(img, img, mask=mask)
    bg_removed = res + (255 - cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))

    # Call body measurement logic
    result = main(bg_removed, height, None)
    return result

# --------------------
# 🔹 CLI for testing
# --------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MobileNetV2 DeepLab TFLite Segmentation")
    parser.add_argument("-i", "--input_dir", type=str, required=True, help="Input image path.")
    parser.add_argument("-ht", "--height", type=int, required=True, help="Height in cm.")
    args = parser.parse_args()
    print(run_inference(args.input_dir, args.height))
