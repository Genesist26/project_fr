#!/usr/bin/env python

from socket import *
import numpy as np
import cv2

host = "192.168.1.6"
port = 4096
buf = 1024
addr = (host, port)
fName = 'img.jpg'
timeOut = 0.05

def foo():
    while True:
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(addr)

        data, address = s.recvfrom(buf)
        f = open(data, 'wb')

        data, address = s.recvfrom(buf)

        try:
            while(data):
                f.write(data)
                s.settimeout(timeOut)
                data, address = s.recvfrom(buf)
        except timeout:
            f.close()
            s.close()
        image = cv2.imread(fName)
        cv2.imshow('recv', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    foo()
    cv2.destroyAllWindows()