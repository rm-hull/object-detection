from typing import Generator
import cv2
import base64
from io import BytesIO
from PIL import Image


def video_frames(video_path: str) -> Generator:
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise IOError("Error opening video file")

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            yield frame

    finally:
        cap.release()
        cv2.destroyAllWindows()


def to_data_url(image) -> str:
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    byte_stream = BytesIO()
    image_pil.save(byte_stream, format="JPEG")
    base64_str = base64.b64encode(byte_stream.getvalue()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{base64_str}"

    return data_url
