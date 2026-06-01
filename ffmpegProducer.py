import subprocess


def main(stream_queue, ffmpeg_queue):
    Width, Height, FPS = 640, 480, 30
    frame = stream_queue.get()

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        f"{Width}x{Height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-f",
        "mp4",
        "-movflags",
        "frag_keyframe+empty_moov",
        "-",
    ]
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        std=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    try:
        while True:
            try:
                frame_bytes = frame
            except Empty:
                continue
            if frame_bytes is None:
                break
            try:
                process.stdin.write(frame_bytes)
                process.stdin.flush()

                encoded_chunk = process.stdout.read(65536)
                if encoded_chunk:
                    ffmpeg_queue.put(encoded_chunk)
            except BrokenPipeError:
                break
    except Exception as e:
        print(e)

    finally:
        if process.stdin:
            process.stdin.close()
        if process.stdout:
            remaining_data = process.stdout.read()
            if remaining_data:
                ffmpeg_queue.put(remaining_data)
            process.stdout.close()
        process.wait()
        ffmpeg_queue.put(None)
