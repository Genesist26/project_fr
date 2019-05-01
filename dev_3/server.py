# PI
import socket
import cv2
import struct ## new
import pickle

def server_program():
    cam = cv2.VideoCapture(0)

    cam.set(3, 640)
    cam.set(4, 480)

    img_counter = 0
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    HOST = '192.168.137.56'
    PORT = 8485

    ## socket_code
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    server_socket.bind((HOST, PORT))
    print('Socket bind complete')
    server_socket.listen(2)
    print('Socket now listening')



    while (True):
        conn, address = server_socket.accept()
        print("Connection from: " + str(address))

        while True:
            ret, frame = cam.read()
            result, frame = cv2.imencode('.jpg', frame, encode_param)
            #    data = zlib.compress(pickle.dumps(frame, 0))
            data = pickle.dumps(frame, 0)
            size = len(data)

            print("{}: {}".format(img_counter, size))
            try:
                conn.sendall(struct.pack(">L", size) + data)
            except:
                print("Socket is dead or Client closeed connection")

                conn.close()  # close the connection
                print("conn.close():\tOK")

                cam.release()
                print("cam.release():\tOK")

                cv2.destroyAllWindows()
                print("cv2.destroyAllWindows():\tOK")

                print("waiting for new client")

                ## hard_code
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print('Socket created')

                server_socket.bind((HOST, PORT))
                print('Socket bind complete')
                server_socket.listen(2)
                print('Socket now listening')

                cam = cv2.VideoCapture(0)

                cam.set(3, 640)
                cam.set(4, 480)

                img_counter = 0
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                break
            img_counter += 1

            # data = conn.recv(1024).decode()
            # if not data:
            #     # if data is not received break
            #     print("client send close request")
            #     break

if __name__ == '__main__':
    server_program()