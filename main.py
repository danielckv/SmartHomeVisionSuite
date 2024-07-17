import signal
import cv2
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

    detector = Detection()
    camera = Camera(0, 960, 256)
    local_stream = VideoStream(config['videoStream']['url'])
    local_stream.start()

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        original_frame = camera.cap.read()[1]

        # Process frame
        frame_with_detections, detected_person = detector.process_frame(original_frame)
        if detected_person:
            object_frame = detector.cut_frame_to_object(original_frame)
            save_frame_to_jpeg(object_frame)

        local_stream.write_frame(frame_with_detections)

        # Display the resulting frame
        if debug:
            cv2.imshow('frame', frame_with_detections)
        if cv2.waitKey(1) & 0xFF == ord('q') or not app_state['running']:
            break

    camera.release()
    local_stream.stop()
    cv2.destroyAllWindows()
