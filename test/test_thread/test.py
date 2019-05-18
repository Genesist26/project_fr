import threading
import time


class UploadStreamThread(threading.Thread):
    running = True

    def run(self):
        print("UploadStreamThread:\tSTART")
        global stream_flag

        while self.running:
            if stream_flag:
                print("x")

            time.sleep(1)

    def stop(self):
        self.running = False


stream_flag = False

us = UploadStreamThread()
us.start()
time.sleep(3)
stream_flag = True
time.sleep(3)
stream_flag = False
time.sleep(3)