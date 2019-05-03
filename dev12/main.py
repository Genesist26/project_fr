import json
import os
import threading
import time
from urllib.request import urlopen
from uuid import getnode as get_mac

import cv2

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
        global cam_name
        global owner
        global key_SN
        global config_SN
        global key
        global group_name
        global group_id
        global location

        i = 0
        while self.running:

            try:
                res = urlopen("http://" + server_ip + ":" + server_port + "/code")
                res_string = json.loads((res.read()).decode("utf-8"))
                print(res_string)
                j_res = json.loads(res_string)

                status = j_res['status']

                if status == 'disable':
                    print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
                    enable_flag = False

                elif status == 'enable':
                    print("RepeatTimerThread [" + str(i) + "]:\tENABLE")
                    enable_flag = True

                    update_flag = False

                    if "key_SN" in j_res:  # new key available
                        update_flag = True
                        enable_flag = False

                        key_SN = j_res["key_SN"]
                        key = j_res["key"]
                        print("New key_SN:\t", key_SN)
                        print("New key:\t", key)

                    if "config_SN" in j_res:  # new config available
                        update_flag = True
                        enable_flag = False

                        config_SN = j_res["config_SN"]
                        if "group_name" in j_res['group_name']:  # handle new group
                            group_name = j_res['group_name']
                            group_id = j_res['group_id']
                            location = j_res['location']

                    if update_flag:
                        print("config_file:\t UPDATING")
                        update_config_file()


            except:
                enable_flag = False
                print("urlopen:\t ERROR")

            i = i + 1
            time.sleep(5)

    def stop(self):
        self.running = False


def update_config_file():
    global enable_flag

    global cam_id
    global cam_name
    global owner
    global key_SN
    global config_SN
    global key
    global group_name
    global group_id
    global location


    global debug_on_window

    if debug_on_window:
        filename = "D:/home/pi/project/project_fr/config.json"        # windows
    else:
        filename = "/home/pi/project/config.json"      # pi

    msg = {
        "cam_id": hex(get_mac()),
        "cam_name": cam_name,
        "owner": owner,
        "key_SN": key_SN,
        "config_SN": config_SN,
        "key": key,
        "group_name": group_name,
        "group_id": group_id,
        "location": location
    }

    with open(filename, 'w') as fp:
        json.dump(msg, fp)

    enable_flag = False


def load_config_file():
    global cam_id
    global cam_name
    global owner
    global key_SN
    global config_SN
    global key
    global group_name
    global group_id
    global location

    global debug_on_window

    if debug_on_window:
        filename = "D:/home/pi/project/project_fr/config.json"  # windows
    else:
        filename = "/home/pi/project/config.json"  # pi
    msg = {
        "cam_id": hex(get_mac()),
        "cam_name": "none",
        "owner": "none",
        "key_SN": "none",
        "config_SN": "none",
        "key": "none",
        "group_name": "none",
        "group_id": "none",
        "location": "none"
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
            cam_name = data["cam_name"]
            owner = data["owner"]
            key_SN = data["key_SN"]
            config_SN = data["config_SN"]
            key = data["key"]
            group_name = data["group_name"]
            group_id = data["group_id"]
            location = data["location"]

            for k in data:
                print(k + ":\t" + data[k])


### var
cam_id = None
cam_name = None
owner = None
key_SN = None
config_SN = None
key = None
group_name = None
group_id = None
location = None

debug_on_window = False


server_ip = "13.76.191.11"
server_port = "8080"

if debug_on_window:
    face_cascade = cv2.CascadeClassifier('C:/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
else:
    face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.4.3/data/haarcascades/haarcascade_frontalface_default.xml')




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
