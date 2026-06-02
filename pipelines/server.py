from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Empty
import threading

def run(ffmpeg_queue):
    class StreamHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                html_content = """<!DOCTYPE html>
                <html><head><title>Live Feed</title>
                <style>body{background:#111;color:#fff;font-family:sans-serif;text-align:center;}</style>
                </head><body>
                <h2>YOLO Pipeline Live Stream</h2>
                <img src="/video" width="640" height="480">
                </body></html>"""
                self.wfile.write(html_content.encode("utf-8"))
            elif self.path == "/video":
                print("video endpoint hit")
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.end_headers()
                while not ffmpeg_queue.empty():
                    try:
                        ffmpeg_queue.get_nowait()
                    except Empty:
                        break
                try:
                    while True:
                        try:
                            chunk = ffmpeg_queue.get(timeout=5)
                        except Empty:
                            continue
                        if chunk is None:
                            break
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                        self.wfile.write(chunk)
                        self.wfile.write(b"\r\n")
                        self.wfile.flush()
                        print(f"chunk written to browser: {len(chunk)} bytes")
                except (ConnectionError, BrokenPipeError):
                    print("client disconnected")
            else:
                self.send_error(404, "not found")

    class ThreadedHTTPServer(HTTPServer):
        def process_request(self, request, client_address):
            thread = threading.Thread(target=self.__process_request, args=(request, client_address))
            thread.daemon = True
            thread.start()
        def __process_request(self, request, client_address):
            self.finish_request(request, client_address)

    try:
        server = ThreadedHTTPServer(("0.0.0.0", 8081), StreamHandler)
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()