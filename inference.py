import cv2

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference


class Inferencer():

    def __init__(self, model: str, labels: str, top_k: int = 3, threshold: float = 0.1):
        self.interpreter = make_interpreter(model)
        self.interpreter.allocate_tensors()
        self.labels = read_label_file(labels)
        self.inference_size = input_size(self.interpreter)
        self.top_k = top_k
        self.threshold = threshold

    def detect(self, cv2_im):
        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, self.inference_size)
        run_inference(self.interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(self.interpreter, self.threshold)[:self.top_k]

        # obj.bbox / obj.score / obj.id
        for obj in objs:
            obj['label'] = self.labels.get(obj.id, obj.id)
