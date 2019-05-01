import cv2
# Playing video from file:
# cap = cv2.VideoCapture('vtest.avi')
# Capturing video from webcam:



# class CameraController:
#
#     def __init__(self, videoDeviceIndex):
#         self.cap = cv2.VideoCapture(videoDeviceIndex)
#         self.b = "world"
#
#     def read(self):
#         return self.cap.read()
#
#     def release(self):
#         self.cap.release()
#
#
#
#
# if __name__ == '__main__':
#     x = CameraController(0)
#     print(x.b)
#     currentFrame = 0
#
#     while (True):
#
#         ret, frame = x.read()
#
#         # Handles the mirroring of the current frame
#         frame = cv2.flip(frame, 1)
#
#         # Our operations on the frame come here
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         # Saves image of the current frame in jpg file
#         # name = 'frame' + str(currentFrame) + '.jpg'
#         # cv2.imwrite(name, frame)
#
#         # Display the resulting frame
#         cv2.imshow('frame',gray)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#         # To stop duplicate images
#         currentFrame += 1
#
#     # When everything done, release the capture
#     x.release()
#     cv2.destroyAllWindows()
#
# # cap = cv2.VideoCapture(0)
# #
# # currentFrame = 0
# # while(True):
# #     # Capture frame-by-frame
# #     ret, frame = cap.read()
# #
# #     # Handles the mirroring of the current frame
# #     frame = cv2.flip(frame, 1)
# #
# #     # Our operations on the frame come here
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #
# #     # Saves image of the current frame in jpg file
# #     # name = 'frame' + str(currentFrame) + '.jpg'
# #     # cv2.imwrite(name, frame)
# #
# #     # Display the resulting frame
# #     cv2.imshow('frame',gray)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break
# #
# #     # To stop duplicate images
# #     currentFrame += 1
# #
# # # When everything done, release the capture
# # cap.release()
# # cv2.destroyAllWindows()


