from typing import Generator
import cv2


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
