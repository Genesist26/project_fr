import json
import os
import threading
import time
from urllib.request import urlopen

import cv2

server_ip = "13.76.191.11"
server_port = "8080"

face_cascade = cv2.CascadeClassifier('C:/opencv/data/haarcascades/haarcascade_frontalface_default.xml')


class CameraReaderThread(threading.Thread):
    running = True

    def __init__(self, camera_index):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_index)
        ret, self.frame = self.cap.read()

    def run(self):
        print("CameraReaderThread:\tSTART")

        global frame_buffer
        while self.running:
            ret, frame_buffer = self.cap.read()

    def stop(self):
        self.running = False
        self.cap.release()


class AzureCallerThread(threading.Thread):
    running = True

    def run(self):
        print("AzureCallerThread:\tSTART")
        global azure_flag
        i = 0
        while self.running:
            if azure_flag:
                lock.acquire()
                azure_flag = False
                lock.release()
                print("AzureCallerThread [" + str(i) + "]")
                i = i + 1

    def stop(self):
        self.running = False


class HaarcascadThread(threading.Thread):
    running = True

    def run(self):
        print("HaarcascadThread:\tSTART")
        time.sleep(1)
        global frame_buffer
        global azure_flag
        last = 0
        i = 0

        while self.running:
            frame = frame_buffer

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            current = len(faces)

            if current == 0:
                last = current
            elif current != last:
                lock.acquire()
                azure_flag = True
                lock.release()

                print("HaarcascadThread found[" + str(i) + ", " + str(current) + "]")
                last = current
                i = i + 1

    def stop(self):
        self.running = False


class FlaskServerThread(threading.Thread):
    running = True

    def run(self):
        print("FlaskServerThread:\tSTART")
        i = 0
        while self.running:
            print("FlaskServerThread [" + str(i) + "]")
            i = i + 1

    def stop(self):
        self.running = False


class RepeatTimerThread(threading.Thread):
    running = True

    def run(self):
        print("RepeatTimerThread:\tSTART")

        i = 0
        while self.running:
            # res = urlopen("http://"+server_ip+":"+server_port+"/code2")
            res = urlopen("http://"+server_ip+":"+server_port+"/code2")

            res_string = json.loads((res.read()).decode("utf-8"))
            j_res = json.loads(res_string)

            status = j_res['status']

            if status == 'enable':
                print("RepeatTimerThread [" + str(i) + "]:\tENABLE")
            elif status == 'disable':

                print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
            else:
                print("RepeatTimerThread [" + str(i) + "]:\tUNKNOWN")

            i = i + 1
            time.sleep(5)

    def stop(self):
        self.running = False


def load_config_file():
    filename = "D:/home/pi/project/project_fr/config.json"

    if os.path.exists(filename):
        print("exists")
        with open(filename) as data_file:
            data = json.load(data_file)
            print(data)
    else:
        print("not exists")


load_config_file()

lock = threading.Lock()

enable_flag = False
azure_flag = False

frame_buffer = None

camera_reader_thread = CameraReaderThread(0)
azure_caller_thread = AzureCallerThread()
haarcascad_thread = HaarcascadThread()
flask_server_thread = FlaskServerThread()
repeat_timer_thread = RepeatTimerThread()

camera_reader_thread.start()
haarcascad_thread.start()
azure_caller_thread.start()
# flask_server_thread.start()
repeat_timer_thread.start()

# time.sleep(2)
# while True:
#     frame = frame_buffer
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#     for (x, y, w, h) in faces:
#         img = cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 0, 0), 2)
#         roi_gray = gray[y:y + h, x:x + w]
#         roi_color = gray[y:y + h, x:x + w]
#
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# camera_reader_thread.stop()
# cv2.destroyAllWindows()
