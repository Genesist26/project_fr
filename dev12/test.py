from dev12.CameraController import CameraController
import cv2

cam = CameraController(0)

while (True):
    # Capture frame-by-frame
    frame = cam.getFram()

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cam.release()
cv2.destroyAllWindows()
