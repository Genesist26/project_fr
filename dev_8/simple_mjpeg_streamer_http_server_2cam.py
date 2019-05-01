#!/usr/bin/python
"""
    Original Author: Igor Maculan - n3wtron@gmail.com
    Modified by: Drunkar - drunkars.p@gmail.com
    A Simple mjpg stream http server
"""
import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO
import time
# from signal import signal, SIGPIPE, SIG_DFL

# signal(SIGPIPE,SIG_DFL)
capture1 = None
# capture2 = None


class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("cam1.mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while True:
                try:
                    rc, img1 = capture1.read()
                    if not rc:
                        continue
                    imgRGB = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = StringIO.StringIO()
                    jpg.save(tmpFile, "JPEG")
                    self.wfile.write("--jpgboundary")
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(tmpFile.len))
                    self.end_headers()
                    jpg.save(self.wfile, "JPEG")
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        elif self.path.endswith("cam2.mjpg"):
            self.send_response(200)
            self.send_header(
                "Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while True:
                try:
                    rc, img2 = capture2.read()
                    if not rc:
                        continue
                    imgRGB = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = StringIO.StringIO()
                    jpg.save(tmpFile, "JPEG")
                    self.wfile.write("--jpgboundary")
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(tmpFile.len))
                    self.end_headers()
                    jpg.save(self.wfile, "JPEG")
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head></head><body>")
            self.wfile.write("<img src='/cam1.mjpg'/>")
            self.wfile.write("<img src='/cam2.mjpg'/>")
            self.wfile.write("</body></html>")
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main():
    global capture1
    capture1 = cv2.VideoCapture(0)
    # capture1.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 960)
    # capture1.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 540)
    # capture1.set(cv2.cv.CV_CAP_PROP_FPS, 3)
    # global capture2
    # capture2 = cv2.VideoCapture(1)
    # capture2.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 960)
    # capture2.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 540)
    # capture2.set(cv2.cv.CV_CAP_PROP_FPS, 3)
    global img1
    try:
        server = ThreadedHTTPServer(("192.168.1.6", 8080), CamHandler)
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        capture1.release()
        # capture2.release()
        server.socket.close()


if __name__ == "__main__":
    main()