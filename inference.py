import cv2

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference


class Inferencer():

    def __init__(self, model: str, labels: str, top_k: int = 3, threshold: float = 0.6):
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
        return get_objects(self.interpreter, self.threshold)[:self.top_k]

    def as_dict_array(self, objs):
        return [
            dict(
                score=obj.score,
                id=obj.id,
                label=self.labels.get(obj.id, obj.id),
                bbox=dict(
                    xmin=obj.bbox.xmin,
                    xmax=obj.bbox.xmax,
                    ymin=obj.bbox.ymin,
                    ymax=obj.bbox.ymax
                )
            )
            for obj in objs
        ]

    def append_objs_to_img(self, cv2_im, objs):
        height, width, _ = cv2_im.shape
        scale_x, scale_y = width / \
            self.inference_size[0], height / self.inference_size[1]
        for obj in objs:
            bbox = obj.bbox.scale(scale_x, scale_y)
            x0, y0 = int(bbox.xmin), int(bbox.ymin)
            x1, y1 = int(bbox.xmax), int(bbox.ymax)

            percent = int(100 * obj.score)
            label = '{}% {}'.format(percent, self.labels.get(obj.id, obj.id))

            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        return cv2_im
