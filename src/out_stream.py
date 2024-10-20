import ffmpeg


class RTSPFrameStreamer:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.ffmpeg_container = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(1270, 720), framerate=25)
            .output(rtsp_url,
                    format='rtsp',
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    preset='ultrafast',
                    tune='zerolatency',
                    rtsp_transport='tcp',
                    r='30',
                    g='30',
                    force_key_frames='expr:gte(t,n_forced*2)',
                    )
            .global_args('-hide_banner', '-loglevel', 'info')
            .run_async(pipe_stdin=True)
        )

    def write_frame(self, frame):
        self.ffmpeg_container.stdin.write(frame)

    def close(self):
        self.ffmpeg_container.stdin.close()
        self.ffmpeg_container.wait()
