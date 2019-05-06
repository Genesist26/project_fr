import datetime
import json

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

data = {'temperature': '24.3'}
data_json = json.dumps(li)
payload = {'json_payload': data_json}
r = requests.post("http://" + server_ip + ":" + server_port + "/code/index.php/api/found", data=payload)
print(r.status_code)
