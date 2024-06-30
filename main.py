import signal
import cv2
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

    detector = Detection()
    camera = Camera(0, 640, 480)

    signal.signal(signal.SIGINT, signal_handler)

    out_camera = cv2.VideoWriter('/dev/video1', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (640, 480))

    while True:
        original_frame = camera.get_frame()

        # Process frame
        frame_with_detections = detector.process_frame(original_frame)
        detected_person = detector.is_person_or_dog(original_frame)
        if detected_person:
            object_frame = detector.cut_frame_to_object(original_frame)
            save_frame_to_jpeg(object_frame)
            print("Person detected. Frame saved.")

        out_camera.write(frame_with_detections)

        # Display the resulting frame
        if debug:
            cv2.imshow('frame', frame_with_detections)
        if cv2.waitKey(1) & 0xFF == ord('q') or not app_state['running']:
            break

    camera.release()
    cv2.destroyAllWindows()
