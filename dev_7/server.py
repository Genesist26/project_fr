# PI
import socket
import cv2
import struct ## new
import pickle
from threading import Thread
from time import sleep
from subprocess import check_output
from flask import Flask, render_template, Response

FRAME_BUFF = None
RET = None
cam = cv2.VideoCapture(0)

functions = [{'describe': 'Azure Camera', 'function_name': 'azure_camera'},
             {'describe': 'Server', 'function_name': 'server_program'}]
class myThread(Thread):
    def __init__(self, func_name):
        Thread.__init__(self)
        # self.thread_id = thread_id
        self.function = func_name

    def run(self):
        print("Starting " + self.name)
        self.function()
        print("Exiting " + self.name)

# class multiSocket(Thread):
#     def __init__(self, c, func_name):
#         Thread.__init__(self)
#         # self.thread_id = thread_id
#         self
#         self.function = func_name
#
#     def run(self):
#         print("Starting " + self.name)
#         self.function()
#         print("Exiting " + self.name)
def browser():
    # browser_thread()
    app = Flask(__name__)
    hostname = socket.gethostname()
    ip_de = socket.gethostbyname(hostname)

    global cap
    # ip = check_output(['hostname', '-I'])
    # ip_de = ip.decode("utf-8")

    @app.route('/')
    def index():
        return render_template('register.html')

    def gen():
        while True:
            if FRAME_BUFF:
                success, image = FRAME_BUFF
                # if image.any:
                # if image == None:
                #     continue
                # if not np.sum(image) == 0:
                ret, jpeg = cv2.imencode('.jpg', image)
                frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                #     cap.release()
                #     cv2.destroyAllWindows()

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host=ip_de)


def camera_reader():
    global FRAME_BUFF
    global cam
    # global RET
    # global cam
    # cam = cv2.VideoCapture(0)

    cam.set(3, 640)
    cam.set(4, 480)

    while True:
        FRAME_BUFF = cam.read()
        # FRAME_BUFF = frame

def server_program():
    # ip = check_output(['hostname', '-I'])   # get ip of IP
    # HOST = ip.decode("utf-8")
    HOST = socket.gethostname()
    PORT = 5000

    ## socket_code
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    server_socket.bind((HOST, PORT))
    print('Socket bind complete')
    server_socket.listen(2)
    print('Socket now listening')



    while True:
        conn, address = server_socket.accept()
        print('Connection from : ' + str(address))
        # print('Connection from : ' + str(conn.getsockname()))
        Thread(target=client_handler, args=(conn, address)).start()

def client_handler(conn, addr):
    global FRAME_BUFF
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    while True:
        if not FRAME_BUFF == None:
            ret, frame = FRAME_BUFF
            result, frame = cv2.imencode('.jpg', frame, encode_param)
            #    data = zlib.compress(pickle.dumps(frame, 0))
            data = pickle.dumps(frame, 0)
            size = len(data)

            # print("{}: {}".format(img_counter, size))
            try:
                conn.sendall(struct.pack(">L", size) + data)
            except:
                conn.close()  # close the connection
                print("client ["+str(addr)+"] disconnectd:\tOK")
                break

if __name__ == '__main__':
    camera_reader = Thread(target=camera_reader, args=())
    camera_reader.start()

    server_program = Thread(target=server_program, args=())
    # server_program.start()

    browser()