# PI
import socket
import cv2
import struct ## new
import pickle
from threading import Thread
from time import sleep
from subprocess import check_output

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


def camera_reader():
    global FRAME_BUFF
    global cam

    cam.set(3, 640)
    cam.set(4, 480)

    while True:
        FRAME_BUFF = cam.read()

def server_program():
    ip = check_output(['hostname', '-I'])   # get ip of IP
    HOST = ip.decode("utf-8")
    # HOST = socket.gethostname()
    PORT = 4000

    ## socket_code
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    server_socket.bind((HOST, PORT))
    print('Socket bind complete')
    server_socket.listen(5)
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
                print('Disconnectd from : ' + str(addr))
                break

if __name__ == '__main__':
    camera_reader = Thread(target=camera_reader, args=())
    camera_reader.start()

    server_program = Thread(target=server_program, args=())
    server_program.start()