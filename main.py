import datetime
import json
import os
import re
import socket
import threading
import time
from subprocess import check_output
from urllib.request import urlopen
from uuid import getnode as get_uuid_mac
from flask_fontawesome import FontAwesome
import cognitive_face as CF
import cv2
import requests
from flask import Flask, request, render_template, Response


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
        global list_buffer
        global debug_on_window
        global project_dirpath

        CF.Key.set(key)
        CF.BaseUrl.set(self.BASE_URL)
        x = 0

        unknown_filepath = project_dirpath + "/unknown.jpg"

        while self.running:
            if enable_flag and azure_flag:
                lock.acquire()
                azure_flag = False
                lock.release()

                x = x + 1
                print("AzureCallerThread [" + str(x) + "]")

                # api
                try:
                    in_frame = cv2.imread(image_path)

                    azure_detect_list = CF.face.detect(image_path)
                    azure_unknown_list = azure_detect_list.copy()
                except Exception as e:
                    self.exception_handler(e)

                face_ids = [d['faceId'] for d in azure_detect_list]

                azure_detect_number = len(face_ids)

                print("azure_detect_number: " + str(azure_detect_number))

                if azure_detect_number:
                    try:
                        azure_identified_list = CF.face.identify(face_ids, group_id)

                    except Exception as e:
                        self.exception_handler(e)

                    azure_known_number = azure_detect_number
                    known_counter = 0

                    current_dt = datetime.datetime.now()
                    timestamp = current_dt.strftime("%Y-%m-%d %H:%M:%S")

                    print("\tazure_known_person:")

                    for i in range(azure_detect_number):
                        candidate = azure_identified_list[i]['candidates']
                        if candidate:  # check empty list
                            candidate_person_id = candidate[0]['personId']
                            candidate_confidence = candidate[0]['confidence']

                            azure_unknown_list = [d for d in azure_unknown_list if
                                                  d['faceId'] != azure_identified_list[i]['faceId']]

                            azure_known_number -= 1

                            for person in person_list:
                                if candidate_person_id in person['person_id']:
                                    known_counter = known_counter + 1

                                    name = person['person_name']

                                    di = {
                                        "name": name,
                                        "confidence": candidate_confidence,
                                        "timestamp": timestamp
                                    }

                                    list_buffer.append(di)

                                    print("\t\t" + str(known_counter) + ": [" + name + "," + str(
                                        candidate_confidence) + "]")

                    if azure_known_number:
                        print("\tazure_unknown_person: " + str(azure_known_number))
                        print(azure_unknown_list)
                        unknown_face_rectangle = [d['faceRectangle'] for d in azure_unknown_list]

                        for face in unknown_face_rectangle:
                            left = face['left']
                            top = face['top']
                            bottom = left + face['height']
                            right = top + face['width']
                            cv2.rectangle(in_frame, (left, top), (bottom, right), (0, 0, 255), 2)

                        cv2.imwrite(unknown_filepath, in_frame)

    def stop(self):
        self.running = False

    def exception_handler(self, e):
        e_msg = str(e)
        status_code = e_msg[e_msg.find(":") + 1:]
        print("status_code =>\t", status_code)
        delay_str = re.search(r'Try again in(.*?)seconds', e_msg).group(1)
        delay = int(delay_str)

        print("Try again in:\t" + str(delay) + " second")
        time.sleep(delay)
        print("RETRY")


class HaarcascadThread(threading.Thread):
    running = True

    def run(self):
        print("HaarcascadThread:\tSTART")
        global frame_buffer
        global azure_flag
        global enable_flag
        global image_path
        global project_dirpath
        img_name = "capture"
        last = 0
        i = 0

        image_path = project_dirpath + img_name + ".jpg"

        while self.running:
            if enable_flag:
                frame = frame_buffer

                faces = face_cascade.detectMultiScale(
                    frame,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(150, 150),
                    flags=0
                )
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

                # time.sleep(3)

    def stop(self):
        self.running = False


class FlaskServerThread(threading.Thread):
    running = True

    def run(self):
        global debug_on_window

        if debug_on_window:
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
        else:
            ip_addr = check_output(['hostname', '-I']).decode('ascii')

        print("FlaskServerThread:\tSTART")

        app = Flask(__name__)
        fa = FontAwesome(app)

        @app.route('/')
        def index():
            dropdown_list = get_essid_list()
            return render_template('register.html', dropdown_list=dropdown_list)

        @app.route('/connect', methods=['POST'])
        def connect():
            global owner
            global cam_name

            ssid = request.form['ssid']
            password = request.form['ssidpsk']
            owner = request.form['owner']
            cam_name = request.form['cam_name']
            print("/connect")
            print("\tssid => ", ssid)
            print("\tpassword => ", password)
            print("\towner => ", owner)
            print("\tcam_name => ", cam_name)

            update_config()
            set_new_ssid(ssid, password)
            return shutdown("Try to connect to SSID: " + ssid + "")

        @app.route('/q')
        def q():
            return shutdown()

        def shutdown(msg):
            global reboot_flag
            shutdown_hook = request.environ.get('werkzeug.server.shutdown')
            if shutdown_hook is not None:
                shutdown_hook()

            reboot_flag = True
            # return Response(msg, mimetype='text/plain')
            return render_template('message.html')

        app.run(host=ip_addr, debug=False)

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
        global key
        global group_id
        global person_list
        global person_sn
        global list_buffer

        i = 0

        if key_sn == 'none':
            print("/reg --->>")
            di = {"cam_id": cam_id, "owner": owner, 'cam_name': cam_name}

            data_json = json.dumps(di)
            payload = {'json_payload': data_json}
            requests.post("http://" + server_ip + ":" + server_port + "/code2/api/reg",
                          data=payload)
        while self.running:
            try:
                url_str = "http://" + server_ip + ":" + server_port + "/code2/api/status?cam_id=" + cam_id + "&key_sn=" + key_sn + "&group_id=" + group_id + "&person_sn=" + str(
                    person_sn)
                print("/status --->>")
                res = urlopen(url_str)
                res_string = json.loads((res.read()).decode("utf-8"))
                j_res = json.loads(res_string)

                # print(j_res)
                status = j_res['status']

                print("RepeatTimerThread [" + str(i) + "]:\t" + status + "")
                i = i + 1
                # if "streaming" in j_res:
                #     streaming = j_res['streaming']
                #     print("implement streaming function")
                #     if streaming:
                #         print("stream streaming")
                #     else:
                #         print("stop streaming")

                if status == "deactivate":
                    enable_flag = False
                    if key_sn != 'none':
                        reset_device()

                elif status == 'disable':
                    enable_flag = False

                elif status == 'enable':
                    if group_id != 'none':
                        enable_flag = True
                    else:
                        enable_flag = False

                if "key_sn" in j_res or "group_id" in j_res or "person_sn" in j_res:
                    enable_flag = False

                    if "key_sn" in j_res:  # new key available
                        key_sn = j_res["key_sn"]
                        key = j_res["key"]
                        print("New key_sn:\t", key_sn)
                        print("New key:\t", key)

                    if "group_id" in j_res:  # new config available
                        group_id = j_res["group_id"]
                        print("New group_id:\t", group_id)

                    if "person_sn" in j_res:  # new config available
                        person_list = j_res["person_list"]
                        person_sn = j_res["person_sn"]
                        print("New person_sn:\t", person_sn)
                        print("New person_list:\t" + str(len(person_list)) + " person")
                        update_person_list()

                    update_config()

            except:
                enable_flag = False
                print("urlopen:\t ERROR [" + url_str + "]")

            # send list_buffer to server
            if len(list_buffer):
                data_json = json.dumps(list_buffer)
                payload = {'json_payload': data_json}
                requests.post("http://" + server_ip + ":" + server_port + "/code2/api/found", data=payload)

                list_buffer = []

            i = i + 1
            time.sleep(5)

    def stop(self):
        self.running = False


def update_config():
    global enable_flag

    global cam_id
    global cam_name
    global owner
    global key_sn
    global key
    global group_id
    global person_list
    global person_sn
    global project_dirpath

    global debug_on_window

    filename = project_dirpath + "/config.json"  # windows

    mac = get_mac()

    config_template = {
        "cam_id": mac,
        "cam_name": cam_name,
        "owner": owner,
        "key_sn": key_sn,
        "key": key,
        "group_id": group_id,
        "person_sn": person_sn,
    }

    with open(filename, 'w') as fp:
        json.dump(config_template, fp)
        fp.close()


def load_config():
    global cam_id
    global cam_name
    global owner
    global key_sn
    global key
    global group_id
    global person_sn
    global project_dirpath

    global debug_on_window

    filename = project_dirpath + "/config.json"  # windows

    mac = get_mac()
    print("mac => ", mac)

    config_template = {
        "cam_id": mac,
        "cam_name": "none",
        "owner": "none",
        "key_sn": "none",
        "key": "none",
        "group_id": "none",
        "person_sn": "none",
    }

    if not os.path.exists(filename):
        print("config:\tNOT EXISTS [CREATING]")

        with open(filename, 'w') as fp:
            json.dump(config_template, fp)
            fp.close()

        print("config:\tCREATING COMPLETED")
        return load_config()

    else:
        print("config:\tEXISTS")
        with open(filename) as data_file:
            data = json.load(data_file)
            data_file.close()

            cam_id = data["cam_id"]
            cam_name = data["cam_name"]
            owner = data["owner"]
            key_sn = data["key_sn"]
            key = data["key"]
            group_id = data["group_id"]
            person_sn = data["person_sn"]

        config_template = {
            "cam_id": mac,
            "cam_name": cam_name,
            "owner": owner,
            "key_sn": key_sn,
            "key": key,
            "group_id": group_id,
            "person_sn": person_sn,
        }

    pp_json_string(config_template)


def load_person_list():
    global person_list
    global project_dirpath

    person_list_filepath = project_dirpath + "/person_list.json"  # windows

    if os.path.exists(person_list_filepath):
        with open(person_list_filepath) as data_file:
            person_list = json.load(data_file)
            data_file.close()


def update_person_list():
    global person_list
    global project_dirpath
    # global group_id

    person_list_filepath = project_dirpath + "/person_list.json"  # windows

    # server_person_url = "http://13.76.191.11:8080/code2/api/all_person/?cam_id=0x1e9cafa9b4&group_id=" + group_id

    # res = urlopen(server_person_url)
    # res_string = json.loads((res.read()).decode("utf-8"))
    # person_list = json.loads(res_string)

    write_json_file(person_list, person_list_filepath)


def pp_json_string(tupple_msg):
    temp = json.dumps(tupple_msg)
    temp2 = json.loads(temp)
    print(json.dumps(temp2, sort_keys=True, indent=4))


def write_json_file(msg, filename):
    with open(filename, 'w') as fp:
        json.dump(msg, fp)
        fp.close()


def get_essid_list():
    global debug_on_window

    ssid_list = []

    if debug_on_window:
        proc = os.popen('netsh wlan show network')
        proc_str = proc.read()
        proc.close()

        proc_res = proc_str.split("\n")
        for x in proc_res:
            if 'SSID' in x:
                temp = x[x.find(":") + 2:]
                ssid_list.append(temp)

    else:
        proc = os.popen('iwlist wlan0 scan | grep ESSID')
        proc_str = proc.read()
        proc.close()

        proc_res = proc_str.split("\n")

        for x in proc_res:
            temp = x[x.find("ESSID") + 7:-1]
            ssid_list.append(temp)

    ssid_list.sort()

    return list(set(ssid_list))


def setup_ap():
    psk = 'project-fr'
    ssid = psk + "-" + get_mac()[-4:]

    access_point = pyaccesspoint.AccessPoint(ssid=ssid, password=psk)
    access_point.stop()
    access_point.start()

    if access_point.is_running():
        print("setup AP:\tOK")
    else:
        print("setup AP:\tFAIL")

    print("\tSSID:\t", ssid)
    print("\tPSK:\t", psk)


def save_register_info():
    print("save_register_info()")

    if not debug_on_window:
        print("shoud execute main function again")


def reboot():
    print("reboot:\t EXECUTING")
    global debug_on_window
    time.sleep(2)

    if debug_on_window:
        print("debug on windows => cannot reboot pi")
        exit()
    else:
        print("reboot pi")
        os.system('reboot')


def check_internet():
    print("checking internet connection:", end='')
    url_str = "http://google.com"
    try:
        urlopen(url_str)
        print("\tOK")
        return True
    except:
        print("\tFAIL")
        return False


def set_new_ssid(new_ssid, new_password):
    global debug_on_window
    global project_dirpath

    if debug_on_window:
        filepath = project_dirpath + "/wpa_supplicant.conf"
    else:
        filepath = "/etc/wpa_supplicant/wpa_supplicant.conf"

    with open(filepath, 'r') as f:
        in_file = f.read()
        f.close()

    if not re.search(r'ssid', in_file):
        msg = "\nnetwork={\n\tssid=\"" + new_ssid + "\"\n\tpsk=\"" + new_password + "\"\n\tkey_mgmt=WPA-PSK\n}"
        in_file = in_file + msg

    out_file = re.sub(r'ssid=".*"', 'ssid=' + '"' + new_ssid + '"', in_file)
    out_file = re.sub(r'psk=".*"', 'psk=' + '"' + new_password + '"', out_file)

    with open(filepath, 'w') as f:
        f.write(out_file)
        f.close()

    print("set new ssid:\tOK")


def boot_mode(mode):
    # print("Boot on Mode:\t", str(mode))

    if mode == 1:
        print("BOOT MODE:\t1")
        if debug_on_window:
            print(">>> debug on windows cannot setup wifi AP <<<")
            flask_server_thread.start()
        else:
            setup_ap()
            flask_server_thread.start()
            while True:

                if reboot_flag:
                    if not debug_on_window:
                        os.system('reboot')
                    else:
                        print("need to reboot [WINDOWS OS]")
                        exit()
                else:
                    time.sleep(3)
    elif mode == 2:
        print("BOOT MODE:\t2")
        os.system('rm /home/pi/project/config.json')
        print("SWITCH MODE TO:\t1")
        return boot_mode(1)
    elif mode == 3:
        print("BOOT MODE:\t3")
        boot_mode(1)
    elif mode == 4:
        print("BOOT MODE:\t4")
        repeat_timer_thread.start()
        time.sleep(2)  # wait for setup key

        camera_reader_thread.start()
        haarcascad_thread.start()
        azure_caller_thread.start()


def reset_device():
    print(">>> RESET DEVIEC <<<")

    global debug_on_window
    global project_dirpath

    if debug_on_window:
        print("remove config.json, person_list.json and restart program!!!")
        os.remove(project_dirpath + "/config.json")
        os.remove(project_dirpath + "/person_list.json")
        exit()
    else:
        set_new_ssid('00000000', '00000000')
        os.system("rm " + project_dirpath + "/config.json")
        os.system("rm " + project_dirpath + "/person_list.json")
        os.system("reboot")


def get_mac(interface='wlan0'):
    global debug_on_window

    if debug_on_window:
        mac = str(hex(get_uuid_mac()))

    else:
        try:
            mac = open('/sys/class/net/%s/address' % interface).read()
            mac = '0x' + ((mac.replace(':', '')).replace("\n", ''))
        except:
            mac_hex_str = "00:00:00:00:00:00"

    return mac[0:17]


def on_windows():
    process = os.popen('hostname')
    proc_res = process.read()
    process.close()

    if "pi" in proc_res:
        return False
    else:
        return True


# azure_var

### global_var
cam_id = None
cam_name = None
owner = None
key_sn = None
key = None
group_id = None
person_list = []
person_sn = None
image_path = None

# debug_var

debug_on_window = on_windows()

if debug_on_window:
    project_dirpath = os.getcwd() + "\\"
else:
    project_dirpath = os.path.dirname(__file__)

print("project_dirpath => ", project_dirpath)
debug_flag = False

if not debug_on_window:
    from PyAccessPoint import pyaccesspoint

print("debug_on_window => ", debug_on_window)

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
list_buffer = []
reboot_flag = False

# initial funtion
load_config()
load_person_list()

camera_reader_thread = CameraReaderThread(0)
azure_caller_thread = AzureCallerThread()
haarcascad_thread = HaarcascadThread()
flask_server_thread = FlaskServerThread()
repeat_timer_thread = RepeatTimerThread()

if check_internet():
    if owner == 'none':
        boot_mode(3)
    else:
        boot_mode(4)
else:
    if owner == 'none':
        boot_mode(1)
    else:
        boot_mode(2)

# if debug_on_window:
#     time.sleep(5)
#     while True:
#         frame = frame_buffer
#         # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         faces = face_cascade.detectMultiScale(
#             frame,
#             scaleFactor=1.1,
#             minNeighbors=5,
#             minSize=(150, 150),
#             flags=0
#         )
#
#         for (x, y, w, h) in faces:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#             roi_gray = frame[y:y + h, x:x + w]
#             roi_color = frame[y:y + h, x:x + w]
#
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     # When everything done, release the capture
#     camera_reader_thread.stop()
#     cv2.destroyAllWindows()
