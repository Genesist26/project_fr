from threading import Thread
from time import sleep
import cv2


def camera_reader():

    global FRAME_BUFF
    global cap

    run = True
    while (run):
        ret, frame = cap.read()
        FRAME_BUFF = frame


FRAME_BUFF = None
cap = cv2.VideoCapture(0)

if __name__ == "__main__":

    thread = Thread(target = camera_reader)
    thread.start()
    sleep(1)

    gray = 1
    FRAME_BUFF = 1
    sleep(1)
    while True:
        frame = FRAME_BUFF
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):

            cap.release()
            cv2.destroyAllWindows()
            break



