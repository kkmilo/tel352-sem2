import tensorflow as tf
import os

import tarfile

TARBALL = r"C:\Users\fevga\Desktop\tel352-sem2\ModuleBodyMeasurements\deeplab_model\deeplabv3_mnv2_pascal_trainval_2018_01_29.tar.gz"
EXTRACT_PATH = "deeplab_model/"

with tarfile.open(TARBALL) as tar:
    tar.extractall(EXTRACT_PATH)


# Paths
FROZEN_GRAPH = r"C:\Users\fevga\Desktop\tel352-sem2\ModuleBodyMeasurements\deeplab_model\deeplabv3_mnv2_pascal_trainval\frozen_inference_graph.pb"
TFLITE_MODEL = "deeplab_mnv2.tflite"

# Load the frozen graph
with tf.io.gfile.GFile(FROZEN_GRAPH, "rb") as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_frozen_graph(
    graph_def_file=FROZEN_GRAPH,
    input_arrays=["ImageTensor"],
    output_arrays=["SemanticPredictions"],
    input_shapes={"ImageTensor": [1, 513, 513, 3]},
)
converter.inference_input_type = tf.uint8  # << set to match frozen graph
converter.inference_output_type = tf.uint8  # optional if output is also uint8
converter.quantized_input_stats = {"ImageTensor": (127.5, 127.5)}

# Optional: float16 quantization for smaller size / faster CPU inference
#converter.optimizations = [tf.lite.Optimize.DEFAULT]
#converter.target_spec.supported_types = [tf.float16]

converter._experimental_lower_int64 = True

tflite_model = converter.convert()

# Save TFLite model
with open(TFLITE_MODEL, "wb") as f:
    f.write(tflite_model)

print("TFLite model saved:", TFLITE_MODEL)
