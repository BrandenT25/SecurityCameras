import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


def main(ffmpeg_queue):

    class StreamHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Live Streaming Feed</title>
                    <style>
                        body { background: #111; color: #fff; font-family: sans-serif; text-align: center; }
                        video { background: #000; border: 2px solid #333; max-width: 100%; height: auto; }
                    </style>
                </head>
                <body>
                    <h2>YOLO Pipeline Live Stream</h2>
                    <video id="player" autoplay controls muted playsinline width="640" height="480">
                        <source src="/video" type="video/mp4; codecs='avc1.42E01E'">
                        Your browser does not support HTML5 streaming video.
                    </video>
                </body>
                </html>
                """
                self.wfile.write(html_content.encode("utf-8"))

            elif self.path == "/video":
                print("Video Endpoint")
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")

                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()

                try:
                    while True:
                        try:
                            chunk = ffmpeg_queue.get(timeout=0.1)
                        except Empty:
                            continue
                        if chunk is None:
                            break

                        chunk_size_header = f"{len(chunk):X}\r\n".encode("utf-8")
                        self.wfile.write(chunk_size_header)
                        self.wfile.write(chunk)
                        self.wfile.write(b"\r\n")
                        self.wfile.flush()

                    self.wfile.write(b"b0\r\n\r\n")
                except (ConnectionError, BrokenPipeError):
                    print("client disconnected")
                except Exception as e:
                    print(e)
            else:
                self.send_error(404, "not found")

    try:
        server = HTTPServer(("0.0.0.0", 8080), StreamHandler)
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
