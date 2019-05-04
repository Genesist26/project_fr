import json
import os
import threading
import time
from urllib.request import urlopen
from uuid import getnode as get_mac

import cognitive_face as CF
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
    BASE_URL = 'https://southeastasia.api.cognitive.microsoft.com/face/v1.0'

    def run(self):
        print("AzureCallerThread:\tSTART")

        global azure_flag
        global enable_flag
        global key
        global person_list
        global image_path

        CF.Key.set(key)
        CF.BaseUrl.set(self.BASE_URL)

        i = 0
        while self.running:
            if enable_flag and azure_flag:
                lock.acquire()
                azure_flag = False
                lock.release()

                # api
                azure_detect_list = CF.face.detect(image_path)
                face_ids = [d['faceId'] for d in azure_detect_list]

                azure_detect_number = len(face_ids)

                print("azure_detect_number: " + str(azure_detect_number))

                if azure_detect_number:
                    azure_identified_list = CF.face.identify(face_ids, group_id)

                    azure_known_number = azure_detect_number
                    known_counter = 0

                    print("\tazure_known_person:")

                    for i in range(azure_detect_number):
                        candidate = azure_identified_list[i]['candidates']
                        if candidate:  # check empty list
                            candidate_personId = candidate[0]['personId']
                            candidate_confidence = candidate[0]['confidence']

                            for person in person_list:
                                if candidate_personId in person['personId']:
                                    known_counter = known_counter + 1
                                    print("\t\t" + str(known_counter) + ": [" + person['name'] + "," + str(
                                        candidate_confidence) + "]")
                                    azure_known_number -= 1

                    if azure_known_number:
                        print("\tazure_unknown_person: " + str(azure_known_number))

                print("AzureCallerThread [" + str(i) + "]")
                i = i + 1

    def stop(self):
        self.running = False

    def sync_person(self):
        global person_list
        global key
        global group_id

        CF.Key.set(key)
        CF.BaseUrl.set(self.BASE_URL)

        person_list = CF.person.lists(group_id)

        if debug_on_window:
            person_list_filepath = "D:/home/pi/project/project_fr/person_list.json"  # windows
        else:
            person_list_filepath = "/home/pi/project/person_list.json"  # pi

        save_msg_to_json(person_list, person_list_filepath)


class HaarcascadThread(threading.Thread):
    running = True

    def run(self):
        print("HaarcascadThread:\tSTART")
        global frame_buffer
        global azure_flag
        global enable_flag
        global image_path
        global immge_name
        img_name = "test4"
        last = 0
        i = 0

        if debug_on_window:
            image_path = "D:/home/pi/project/project_fr/image/" + img_name + ".jpg"
        else:
            image_path = "/home/pi/project" + img_name + ".jpg"

        while self.running:
            if enable_flag:
                frame = frame_buffer

                faces = face_cascade.detectMultiScale(frame, 1.3, 5)
                current = len(faces)

                if current == 0:
                    last = current
                elif current != last:
                    cv2.imwrite(image_path, frame)
                    lock.acquire()
                    azure_flag = True
                    lock.release()

                    print("HaarcascadThread found[" + str(i) + ", " + str(current) + "]")
                    last = current
                    i = i + 1

                time.sleep(0.3)

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
        global debug_flag

        global enable_flag

        global cam_id
        global cam_name
        global owner
        global key_sn
        global config_sn
        global key
        global group_name
        global group_id
        global location
        global person_list
        global person_list_sn

        i = 0
        while self.running:

            try:
                # res = urlopen("http://" + server_ip + ":" + server_port + "/code")
                url_str = "http://" + server_ip + ":" + server_port + "/code/index.php/api/status?cam_id=" + cam_id + "&key_sn=" + key_sn + "&config_sn=" + config_sn + ""
                # url_str = "http://" + server_ip + ":" + server_port + "/code/index.php/api/status?cam_id=" + cam_id + "&key_sn=" + key_sn + "&config_sn=" + config_sn + "&person_list_sn" + person_list_sn + ""
                print(url_str)

                if debug_flag:
                    print("cam_id:\t" + cam_id)
                    print("key_sn:\t" + key_sn)
                    print("config_sn:\t" + config_sn)
                    print("url_str:\t" + url_str)

                res = urlopen(url_str)
                res_string = json.loads((res.read()).decode("utf-8"))
                print(res_string)
                j_res = json.loads(res_string)

                status = j_res['status']

                update_flag = False

                if status == 'disable':
                    print("RepeatTimerThread [" + str(i) + "]:\tDISABLE")
                    enable_flag = False

                elif status == 'enable':
                    enable_flag = True
                    print("RepeatTimerThread [" + str(i) + "]:\tENABLE")

                    if "key_sn" in j_res or "config_sn" in j_res or "person_list_sn" in j_res:
                        enable_flag = False
                        update_flag = True

                        if "key_sn" in j_res:  # new key available
                            key_sn = j_res["key_sn"]
                            key = j_res["key"]
                            print("New key_sn:\t", key_sn)
                            print("New key:\t", key)

                        if "config_sn" in j_res:  # new config available
                            config_sn = j_res["config_sn"]
                            print("New config_sn:\t", config_sn)

                            if "group_name" in j_res:  # handle new group
                                group_name = j_res['group_name']
                                group_id = j_res['group_id']
                                print("New group_name:\t", group_name)
                                print("New group_id:\t", group_id)

                            if "location" in j_res:  # handle new group
                                location = j_res['location']
                                print("New location:\t", location)

                        if "person_list_sn" in j_res:  # new config available
                            person_list_sn = j_res['person_list_sn']
                            person_list = j_res['person_list']
                            print("New person_list_sn:\t", person_list_sn)
                            update_person_list()

                if update_flag:
                    update_config()
                    update_person_list()  # debug only (wait for server side ready)
                    enable_flag = True
            except:
                enable_flag = False
                print("urlopen:\t ERROR")

            i = i + 1
            time.sleep(10)

    def stop(self):
        self.running = False


def update_config():
    global enable_flag

    global cam_id
    global cam_name
    global owner
    global key_sn
    global config_sn
    global key
    global group_name
    global group_id
    global location
    global person_list_sn
    global person_list

    global debug_on_window

    if debug_on_window:
        filename = "D:/home/pi/project/project_fr/config.json"  # windows
    else:
        filename = "/home/pi/project/config.json"  # pi

    msg = {
        "cam_id": hex(get_mac()),
        "cam_name": cam_name,
        "owner": owner,
        "key_sn": key_sn,
        "config_sn": config_sn,
        "person_list_sn": person_list_sn,
        "key": key,
        "group_name": group_name,
        "group_id": group_id,
        "location": location,
    }

    with open(filename, 'w') as fp:
        json.dump(msg, fp)

    print("------------Updating config:\tSTART------------")
    pp_json_string(msg)
    print("------------Updating config:\tFINISH------------")


def load_config():
    global cam_id
    global cam_name
    global owner
    global key_sn
    global config_sn
    global key
    global group_name
    global group_id
    global location
    global person_list_sn

    global debug_on_window

    if debug_on_window:
        filename = "D:/home/pi/project/project_fr/config.json"  # windows
    else:
        filename = "/home/pi/project/config.json"  # pi
    msg = {
        "cam_id": hex(get_mac()),
        "cam_name": "none",
        "owner": "none",
        "key_sn": "none",
        "config_sn": "none",
        "person_list_sn": "none",
        "key": "none",
        "group_name": "none",
        "group_id": "none",
        "location": "none",
    }

    if not os.path.exists(filename):
        print("config:\tNOT EXISTS [CREATING]")

        with open(filename, 'w') as fp:
            json.dump(msg, fp)

        print("config:\tCREATING COMPLETED")
        return load_config()

    else:
        print("config:\tEXISTS")
        with open(filename) as data_file:
            data = json.load(data_file)

            cam_id = data["cam_id"]
            cam_name = data["cam_name"]
            owner = data["owner"]
            key_sn = data["key_sn"]
            config_sn = data["config_sn"]
            person_list_sn = data["person_list_sn"]
            key = data["key"]
            group_name = data["group_name"]
            group_id = data["group_id"]
            location = data["location"]

        msg = {
            "cam_id": hex(get_mac()),
            "cam_name": cam_name,
            "owner": owner,
            "key_sn": key_sn,
            "config_sn": config_sn,
            "key": key,
            "group_name": group_name,
            "group_id": group_id,
            "location": location,
            "person_list_sn": person_list_sn,

        }

    # pretty print json string
    pp_json_string(msg)


def load_person_list():
    global person_list

    if debug_on_window:
        person_list_filepath = "D:/home/pi/project/project_fr/person_list.json"  # windows
    else:
        person_list_filepath = "/home/pi/project/person_list.json"  # pi

    if os.path.exists(person_list_filepath):
        with open(person_list_filepath) as data_file:
            person_list = json.load(data_file)


def update_person_list():
    azure_caller_thread.sync_person()  # debug only

    global person_list
    global key
    global group_id

    if debug_on_window:
        person_list_filepath = "D:/home/pi/project/project_fr/person_list.json"  # windows
    else:
        person_list_filepath = "/home/pi/project/person_list.json"  # pi

    save_msg_to_json(person_list, person_list_filepath)


def pp_json_string(tupple_msg):
    temp = json.dumps(tupple_msg)
    temp2 = json.loads(temp)
    print(json.dumps(temp2, sort_keys=True, indent=4))


def save_msg_to_json(msg, filename):
    if not os.path.exists(filename):
        print("save_msg_to_json:\tNOT EXISTS [CREATING]")

        with open(filename, 'w') as fp:
            json.dump(msg, fp)


# azure_var

### global_var
cam_id = None
cam_name = None
owner = None
key_sn = None
config_sn = None
key = None
group_name = None
group_id = None
location = None
person_list = []
person_list_sn = None
image_path = None

# debug_var
debug_on_window = True
debug_flag = False

# server_var
server_ip = "13.76.191.11"
server_port = "8080"

# harcas_var
if debug_on_window:
    face_cascade = cv2.CascadeClassifier('C:/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
else:
    face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.4.3/data/haarcascades/haarcascade_frontalface_default.xml')

lock = threading.Lock()

enable_flag = False
azure_flag = False

frame_buffer = None

### initial funtion
load_config()
load_person_list()

camera_reader_thread = CameraReaderThread(0)
azure_caller_thread = AzureCallerThread()
azure_caller_thread = AzureCallerThread()
haarcascad_thread = HaarcascadThread()
flask_server_thread = FlaskServerThread()
repeat_timer_thread = RepeatTimerThread()

camera_reader_thread.start()
haarcascad_thread.start()
azure_caller_thread.start()
repeat_timer_thread.start()
# flask_server_thread.start()

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
