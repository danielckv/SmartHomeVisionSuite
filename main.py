import signal
import cv2
import pyvirtualcam

from src.camera import Camera
from src.detection import Detection
from src.utils import save_frame_to_jpeg, load_config_yaml

app_state = {
    'camera': None,
    'detector': None,
    'running': True,
    'zeromq': None
}


def signal_handler(sig, last_frame=None):
    app_state['running'] = False
    print(f"Signal {sig} received. Exiting...")


if __name__ == "__main__":
    config = load_config_yaml()
    debug = config['debug']

    signal.signal(signal.SIGINT, signal_handler)
    detector = Detection()
    camera = Camera(0, 1280, 720)
    with pyvirtualcam.Camera(width=640, height=360, fps=15) as cam:
        while True:
            ret, original_frame = camera.cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting...")
                break

            original_frame = cv2.resize(original_frame, (640, 360))

            # Process frame
            frame_with_detections, detected_person, detections = detector.process_frame(original_frame)
            if detected_person:
                original_frame = frame_with_detections
                to_save = detector.cut_frame_to_object(original_frame, detections)
                print("Person detected!")
                save_frame_to_jpeg(to_save)

            cam.send(original_frame)

            # Sleep until the next frame time
            cam.sleep_until_next_frame()

            # Display the resulting frame
            if debug:
                cv2.imshow('frame', frame_with_detections)
            if cv2.waitKey(1) & 0xFF == ord('q') or not app_state['running']:
                break

    camera.release()
    cv2.destroyAllWindows()
