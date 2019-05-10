import os
import time
proc = os.popen('netsh wlan show network')
proc_str = proc.read()
proc.close()

proc_res = proc_str.split("\n")
for x in proc_res:
    if 'SSID' in x:
        temp = x[9:]
        print(temp)
        time.sleep(1)
