import subprocess


class VideoStream:
    def __init__(self, url):
        self.url = url
        self.stream_name = url.split('/')[-1]
        print("VideoStream object created.")
        print(f"URL: {self.url}")
        print(f"Stream Name: {self.stream_name}")
        self.process_thread = None

    def start(self, codec="h264", bitrate="1M"):
        print(f"Starting video stream from {self.url}...")
        if self.process_thread is None:
            command = [
                "ffmpeg",
                "-f", "rawvideo",
                "-pixel_format", "bgr24",
                "-video_size", f"960x256",
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

    def write_frame(self, frame):
        if self.process_thread:
            self.process_thread.stdin.write(frame.tostring())
            self.process_thread.stdin.flush()
        else:
            print("Video stream is not running. Cannot write frame.")
            exit(1)

    def stop(self):
        print("Stopping video stream...")
        if self.process_thread:
            self.process_thread.terminate()
            self.process_thread = None
        print("Video stream stopped.")
