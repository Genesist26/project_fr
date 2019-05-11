import cv2


class CameraController:

    def __init__(self, cam_index):
        self.cap = cv2.VideoCapture(cam_index)
        self.color_type = cv2.COLOR_BGR2GRAY

    def getFram(self):
        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray