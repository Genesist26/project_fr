# server_var
import datetime
from urllib.request import urlopen
import urllib.request

import requests

server_ip = "13.76.191.11"
server_port = "8080"

currentDT = datetime.datetime.now()
timestamp = currentDT.strftime("%Y-%m-%d %H:%M:%S")

name = 'gene'
candidate_confidence = '0.7842'
di = {
    "name": name,
    "confidense": candidate_confidence,
    "timestamp": timestamp
}

li =[]

li.append(di)
li.append(di)
#
# cam_id = "0x00001111"
# # x = requests.post("http://" + server_ip + ":" + server_port + "/code/index.php/api/found?cam_id="+cam_id+"", json=li)
# x = requests.post("http://" + server_ip + ":" + server_port + "/code/index.php/api/found", json=li)
# print(x.status_code)
# print(x.json())

postData = {
#put you post data here
}
r = requests.post("http://play.pokemonshowdown.com/action.php", data=postData)
print(r.text)
print(r.json())
