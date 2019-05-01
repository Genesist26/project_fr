import socket
from threading import Thread
from flask import Flask, render_template, Response
import cv2

from subprocess import check_output

FRAME_BUFF = None
RET = None


class myThread(Thread):
    def __init__(self, func_name):
        Thread.__init__(self)
        # self.thread_id = thread_id
        self.function = func_name

    def run(self):
        print("Starting " + self.name)
        self.function()
        print("Exiting " + self.name)

class Camera_Controller(Thread):


    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    def __init__(self, func_name):
        Thread.__init__(self)
        self.running = True

    def run(self):
        global FRAME_BUFF

        print("camera_reader_thread:\t START")
        while self.running:
            FRAME_BUFF = cam.read()

        print("Exiting " + self.name)

    def stop(self):
        self.running = False
        print("run = False")



def browser():
    app = Flask(__name__)

    # pc
    hostname = socket.gethostname()
    ip_de = socket.gethostbyname(hostname)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host=ip_de, port=8001, debug=False)


def gen():
    global FRAME_BUFF

    while True:
        success, frame = FRAME_BUFF
        ret, jpeg = cv2.imencode('.jpg', frame)
        image = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n\r\n')





def camera_reader():
    global FRAME_BUFF
    global cam
    global capture_frame

    cam.set(3, 640)
    cam.set(4, 480)

    while capture_frame:
        FRAME_BUFF = cam.read()


# main_code


if __name__ == '__main__':
    # Pi
    # ip = check_output(['hostname', '-I'])
    # ip_de = ip.decode("utf-8")


    # # pc
    # hostname = socket.gethostname()
    # ip_de = socket.gethostbyname(hostname)

    cam_thread = Camera_Controller("Camera_Controller_Thread")
    cam_thread.start()




    flask_thread = Thread(target=browser)
    flask_thread.start()

    # app.run(host=ip_de, port=8001, debug=False)
    while(True):
        x = input("get me some character")
        if x == 'q':
            cam_thread.stop()
            break


        print("you was enter "+ x)


    print("end main")
