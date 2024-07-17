import signal
import cv2
import pyvirtualcam

from src.camera import Camera
from src.detection import Detection
from src.stream import VideoStream
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
    camera = Camera(0, 1280, 960)
    with pyvirtualcam.Camera(width=1280, height=960, fps=20) as cam:
        while True:
            ret, original_frame = camera.cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting...")
                break

            # Process frame
            frame_with_detections, detected_person = detector.process_frame(original_frame)
            if detected_person:
                original_frame = detector.cut_frame_to_object(original_frame)
                print("Person detected!")
                save_frame_to_jpeg(original_frame)

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
