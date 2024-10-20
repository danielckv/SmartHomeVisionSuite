import signal
import cv2
from camera import Camera
from detection import Detection
from out_stream import RTSPFrameStreamer
from utils import save_frame_to_jpeg, load_config_yaml

app_state = {
    'camera': None,
    'detector': None,
    'running': True,
    'zeromq': None
}


def signal_handler(sig, last_frame=None):
    app_state['running'] = False
    print(f"Signal {sig} received. Exiting...")


def main():
    config = load_config_yaml()
    debug = config['debug']

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    signal.signal(signal.SIGINT, signal_handler)
    detector = Detection()
    camera = Camera(0, 1280, 720)
    output_stream = RTSPFrameStreamer("rtsp://localhost:8554/detections")
    while True:
        ret, original_frame = camera.cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting...")
            break

        original_frame = cv2.resize(original_frame, (740, 420))

        # Process frame
        frame_with_detections, detected_person, detections = detector.process_frame(original_frame)
        if detected_person:
            original_frame = frame_with_detections
            to_save = detector.cut_frame_to_object(original_frame, detections)
            print("Person detected!")
            save_frame_to_jpeg(to_save)

        yuv_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2YUV)
        yuv_frame[:, :, 0] = clahe.apply(yuv_frame[:, :, 0])
        original_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR)

        output_stream.write_frame(original_frame)

        # Display the resulting frame
        if debug:
            cv2.imshow('frame', frame_with_detections)
        if cv2.waitKey(1) & 0xFF == ord('q') or not app_state['running']:
            break

    output_stream.close()
    camera.release()
    cv2.destroyAllWindows()
