import os
import time

import cv2
import requests

cap = cv2.VideoCapture(0)
dirname = os.path.dirname(__file__)
filepath = dirname + '/image.jpg'


def post_image(filepath):
    global frame
    files = {
        'file': ('0x1e9cafa9b4.jpg', open(filepath, 'rb'), '.jpg'),
    }

    response = requests.post('http://localhost/code2/upload/stream', files=files)
    # response = requests.post('http://13.76.191.11:8080/code2/upload/stream', files=files)
    print(response.json())
    # time.sleep(1)


while (True):
    ret, frame = cap.read()
    gray = frame
    cv2.imwrite(filepath, frame)
    try:
        post_image(filepath)
    except:
        pass
    # time.sleep(0.5)

cap.release()
