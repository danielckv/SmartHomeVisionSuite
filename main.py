import cv2  # OpenCV
from src.camera import Camera
from src.detection import Detector  # Your TensorFlow detector

# ...

if __name__ == "__main__":
    # Load configurations
    # Initialize cameras
    detector = Detector(...)
    camera = Camera(0, 640, 480)

    while True:
        frame = camera.get_frame()
