import subprocess
import cv2


class VideoStream:
    def __init__(self, url):
        self.url = url
        self.stream_name = url.split('/')[-1]
        print("VideoStream object created.")
        print(f"URL: {self.url}")
        print(f"Stream Name: {self.stream_name}")
        self.process_thread = None
        self.local_server_instance = None

    def start_local_server(self):
        self.local_server_instance = cv2.VideoWriter('appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay name=pay0 pt=96 ! application/x-rtp,media=video,encoding-name=H264,payload=96 ! rtspclientsink location=rtsp://127.0.0.1:8554/mystream', cv2.CAP_GSTREAMER, 0, 20, (640, 480), True)

        print("Local server started.")

    def send_frame_to_local_server(self, frame):
        self.local_server_instance.write(frame)

    def start(self, codec="h264", bitrate="2M"):
        print(f"Starting video stream from {self.url}...")
        if self.process_thread is None:
            command = [
                "ffmpeg",
                "-f", "rawvideo",
                "-pixel_format", "bgr24",
                "-video_size", f"1280x960",
                "-framerate", str(25),
                "-i", "-",
                "-c:v", codec,
                "-preset", "veryfast",
                "-g", str(20),
                "-f", "rtsp",
                self.url
            ]
            if bitrate:
                command.extend(["-b:v", str(bitrate)])
            self.process_thread = subprocess.Popen(command, stdin=subprocess.PIPE)

        print("Video stream started.")

    async def write_frame(self, frame):
        if self.process_thread:
            self.process_thread.stdin.write(frame.tostring())
            self.process_thread.stdin.flush()
        else:
            print("Video stream is not running. Cannot write frame.")

    def stop(self):
        print("Stopping video stream...")
        if self.process_thread:
            self.process_thread.terminate()
            self.process_thread = None

        if self.local_server_instance:
            self.local_server_instance.release()
            self.local_server_instance = None
        print("Video stream stopped.")
