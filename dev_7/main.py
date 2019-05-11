import socket
from threading import Thread
from flask import Flask, render_template, Response
import cv2

from subprocess import check_output

app = Flask(__name__)

FRAME_BUFF = None
RET = None
cam = cv2.VideoCapture(0)


@app.route('/')
def index():
    return render_template('register.html')


def gen():
    global FRAME_BUFF

    while True:
        success, frame = FRAME_BUFF
        ret, jpeg = cv2.imencode('.jpg', frame)
        image = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')



def camera_reader():
    global FRAME_BUFF
    global cam

    cam.set(3, 640)
    cam.set(4, 480)

    while True:
        FRAME_BUFF = cam.read()


# main_code


if __name__ == '__main__':
    # Pi
    # ip = check_output(['hostname', '-I'])
    # ip_de = ip.decode("utf-8")


    # pc
    hostname = socket.gethostname()
    ip_de = socket.gethostbyname(hostname)


    camera_reader = Thread(target=camera_reader, args=())
    camera_reader.start()


    app.run(host=ip_de, port=8001, debug=False)
    print("end")