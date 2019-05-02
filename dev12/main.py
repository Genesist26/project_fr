import json
import os
import threading
import time
from urllib.request import urlopen
from uuid import getnode as get_mac

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
        global enable_flag

        i = 0
        while self.running:
            if enable_flag and azure_flag:
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
        global frame_buffer
        global azure_flag
        global enable_flag
        last = 0
        i = 0

        while self.running:
            if enable_flag:
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
        global enable_flag
        global cam_id
        global key_SN
        global config_SN

        i = 0
        while self.running:

            ## test part
            try:
                res = urlopen(
                    "http://13.67.93.241:8080/status?mac=" + cam_id + "&key_SN=" + key_SN + "&config_SN=" + config_SN)
                j_result = json.load(res)
                status = j_result['status']

                if status == 'enable':
                    print("RepeatTimerThread [" + str(i) + "]:\tENABLE")
                    enable_flag = True

                elif status == 'disable':
                    print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
                    enable_flag = False

            except:
                enable_flag = False
                print("urlopen:\t ERROR")

            ## genesis part
            # res = urlopen("http://13.67.93.241:8080/status")
            # j_result = json.load(res)
            # status = j_result['status']
            #
            # if status == 'enable':
            #     print("RepeatTimerThread [" + str(i) + "]:\tENABLE")
            #     enable_flag = True
            #
            # elif status == 'disable':
            #     print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
            #     enable_flag = False

            ## nalina part
            # res = urlopen("http://" + server_ip + ":" + server_port + "/code2")
            # res_string = json.loads((res.read()).decode("utf-8"))
            # print(res_string)
            # j_res = json.loads(res_string)
            #
            #
            # print(j_res)
            #
            # status = j_res['status']
            #
            # if status == 'disable':
            #     print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
            #     pass
            # elif status == 'enable':
            #     print("RepeatTimerThread [" + str(i) + "]:\tENABLE")

            i = i + 1
            time.sleep(5)

    def stop(self):
        self.running = False


def load_config_file():
    global cam_id
    global key_SN
    global key
    global config_SN
    global group_name
    global group_id

    filename = "D:/home/pi/project/project_fr/config.json"

    msg = {
        "cam_id": hex(get_mac()),
        "cam_name": "none",
        "owner": "none",
        "key_SN": "none",
        "config_SN": "none",
        "location": "location1",
        "group_name": "groupName1",
        "group_id": "groupId1",
        "key": "none"
    }
    if not os.path.exists(filename):
        print("config:\tNOT EXISTS [CREATING]")

        with open(filename, 'w') as fp:
            json.dump(msg, fp)

        print("config:\tCREATING COMPLETED")

    else:
        print("config:\tEXISTS")
        with open(filename) as data_file:
            data = json.load(data_file)

            cam_id = data["cam_id"]
            key_SN = data["key_SN"]
            key = data["key"]
            config_SN = data["config_SN"]
            group_name = data["group_name"]
            group_id = data["group_id"]


### var
cam_id = None
key_SN = None
key = None
config_SN = None
group_name = None
group_id = None

lock = threading.Lock()

enable_flag = False
azure_flag = False

frame_buffer = None

### initial funtion
load_config_file()

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
