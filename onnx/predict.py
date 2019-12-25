# The steps implemented in the object detection sample code: 
# 1. for an image of width and height being (w, h) pixels, resize image to (w', h'), where w/h = w'/h' and w' x h' = 262144
# 2. resize network input size to (w', h')
# 3. pass the image to network and do inference
# (4. if inference speed is too slow for you, try to make w' x h' smaller, which is defined with DEFAULT_INPUT_SIZE (in object_detection.py or ObjectDetection.cs))
import sys
import onnx
import onnxruntime
import numpy as np
from PIL import Image, ImageDraw
from object_detection import ObjectDetection
from onnxruntime.capi.onnxruntime_pybind11_state import InvalidArgument

MODEL_FILENAME = 'model.onnx'
LABELS_FILENAME = 'labels.txt'

class ONNXRuntimeObjectDetection(ObjectDetection):
    """Object Detection class for ONNX Runtime"""
    def __init__(self, model_filename, labels):
        super(ONNXRuntimeObjectDetection, self).__init__(labels)
        self.session = onnxruntime.InferenceSession(model_filename)
        self.input_name = self.session.get_inputs()[0].name
        self.is_fp16 = self.session.get_inputs()[0].type == 'tensor(float16)'
        
    def predict(self, preprocessed_image):
        inputs = np.array(preprocessed_image, dtype=np.float32)[np.newaxis,:,:,(2,1,0)] # RGB -> BGR
        inputs = np.ascontiguousarray(np.rollaxis(inputs, 3, 1))

        if self.is_fp16:
            inputs = inputs.astype(np.float16)

        outputs = self.session.run(None, {self.input_name: inputs})
        return np.squeeze(outputs).transpose((1,2,0)).astype(np.float32)

def main(image_filename):
    # Load labels
    with open(LABELS_FILENAME, 'r') as f:
        labels = [l.strip() for l in f.readlines()]

    od_model = ONNXRuntimeObjectDetection(MODEL_FILENAME, labels)

    #image = Image.open(image_filename)

    #image_filename = "vest1.jpg"


    image = Image.open(image_filename)
    print(image.size)
    
    #predictions = od_model.predict_image(image)
    #print(predictions)

    print("numpy:", np.__version__)
    print("onnx: ", onnx.__version__)
    print("onnxruntime: ", onnxruntime.__version__)

    try:
        predictions = od_model.predict_image(image)
        print(predictions)
    except (RuntimeError, InvalidArgument) as e:
        print("ERROR with Shape={0} - {1}".format(image.size, e))
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('USAGE: {} image_filename'.format(sys.argv[0]))
    else:
        main(sys.argv[1])