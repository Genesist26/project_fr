





















from PyAccessPoint import pyaccesspoint
import time
access_point = pyaccesspoint.AccessPoint()
access_point.stop()
access_point.start()

while(access_point.is_running()):
    print("running")
    time.sleep(5)
