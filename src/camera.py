import cv2
import numpy as np


class Camera:
    def __init__(self, camera_id: int, width: int, height: int):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self) -> np.ndarray:
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError(f"Failed to read frame from camera {self.camera_id}")
        return frame

    def release(self):
        self.cap.release()