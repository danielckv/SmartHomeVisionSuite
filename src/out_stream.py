import av


class RTSPFrameStreamer:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.container = av.open(rtsp_url, mode='w')

    def write_frame(self, frame):
        stream = self.container.streams.video[0]
        frame_to_stream = av.VideoFrame.from_ndarray(frame, format='bgr24')
        for packet in stream.encode(frame_to_stream.pts):
            self.container.mux(packet)

    def close(self):
        for stream in self.container.streams:
            for packet in stream.close():
                self.container.mux(packet)
        self.container.close()
