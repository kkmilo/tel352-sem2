import os
import tarfile
import urllib.request
import numpy as np
from PIL import Image
import cv2
import tensorflow as tf
from ModuleBodyMeasurements.demo import main  

# --------------------
# 🔹 Global model cache
# --------------------
MODEL = None

class DeepLabModel(object):
    """Class to load Deeplab model and run inference."""

    INPUT_TENSOR_NAME = 'ImageTensor:0'
    OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
    INPUT_SIZE = 513
    FROZEN_GRAPH_NAME = 'frozen_inference_graph'

    def __init__(self, tarball_path):
        self.graph = tf.Graph()
        graph_def = None
        with tarfile.open(tarball_path) as tar_file:
            for tar_info in tar_file.getmembers():
                if self.FROZEN_GRAPH_NAME in os.path.basename(tar_info.name):
                    file_handle = tar_file.extractfile(tar_info)
                    graph_def = tf.compat.v1.GraphDef()  # TF2 compatibility
                    graph_def.ParseFromString(file_handle.read())
                    break

        if graph_def is None:
            raise RuntimeError('Cannot find inference graph in tar archive.')

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name='')

        self.sess = tf.compat.v1.Session(graph=self.graph)

    def run(self, image):
        width, height = image.size
        resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
        target_size = (int(resize_ratio * width), int(resize_ratio * height))
        resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
        batch_seg_map = self.sess.run(
            self.OUTPUT_TENSOR_NAME,
            feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
        seg_map = batch_seg_map[0]
        return resized_image, seg_map


def create_pascal_label_colormap():
    colormap = np.zeros((256, 3), dtype=int)
    ind = np.arange(256, dtype=int)
    for shift in reversed(range(8)):
        for channel in range(3):
            colormap[:, channel] |= ((ind >> channel) & 1) << shift
        ind >>= 3
    return colormap


def label_to_color_image(label):
    if label.ndim != 2:
        raise ValueError('Expect 2-D input label')
    colormap = create_pascal_label_colormap()
    if np.max(label) >= len(colormap):
        raise ValueError('label value too large.')
    return colormap[label]


# --------------------
# 🔹 Inference entrypoint
# --------------------
def run_inference(image_path: str, height: int):
    global MODEL

    MODEL_NAME = 'xception_coco_voctrainval'
    _DOWNLOAD_URL_PREFIX = 'http://download.tensorflow.org/models/'
    _MODEL_URLS = {
        'mobilenetv2_coco_voctrainaug': 'deeplabv3_mnv2_pascal_train_aug_2018_01_29.tar.gz',
        'mobilenetv2_coco_voctrainval': 'deeplabv3_mnv2_pascal_trainval_2018_01_29.tar.gz',
        'xception_coco_voctrainaug': 'deeplabv3_pascal_train_aug_2018_01_04.tar.gz',
        'xception_coco_voctrainval': 'deeplabv3_pascal_trainval_2018_01_04.tar.gz',
    }
    _TARBALL_NAME = _MODEL_URLS[MODEL_NAME]

    # 🔹 Base directory of this script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Model directory
    model_dir = os.path.join(BASE_DIR, 'deeplab_model')
    os.makedirs(model_dir, exist_ok=True)
    download_path = os.path.join(model_dir, _TARBALL_NAME)

    if not os.path.exists(download_path):
        print(f"Downloading model to {download_path}...")
        urllib.request.urlretrieve(_DOWNLOAD_URL_PREFIX + _MODEL_URLS[MODEL_NAME], download_path)
        print("Download complete!")

    if MODEL is None:
        print("Loading DeepLab model into memory (this happens only once)...")
        MODEL = DeepLabModel(download_path)
        print("Model loaded successfully!")

    # 🔹 Open image using absolute path
    image_abs_path = os.path.join(os.getcwd(), image_path) if not os.path.isabs(image_path) else image_path
    image = Image.open(image_abs_path)
    res_im, seg = MODEL.run(image)

    seg = cv2.resize(seg.astype(np.uint8), image.size)
    mask_sel = (seg == 15).astype(np.float32)
    mask = 255 * mask_sel.astype(np.uint8)

    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    res = cv2.bitwise_and(img, img, mask=mask)
    bg_removed = res + (255 - cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))

    # 🔹 Call body measurement logic
    result = main(bg_removed, height, None)

    return result


# CLI support for testing
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Deeplab Segmentation')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Input image path.')
    parser.add_argument('-ht', '--height', type=int, required=True, help='Height in cm.')
    args = parser.parse_args()
    print(run_inference(args.input_dir, args.height))
