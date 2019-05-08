# server_var
import json
from urllib.request import urlopen

server_ip = "13.76.191.11"
server_port = "8080"

cam_id = '0x1e9cafa9b4'
key_sn = 'none'
group_sn = 'none'

url_str = "http://" + server_ip + ":" + server_port + "/code/index.php/api/status?cam_id=" + cam_id + "&key_sn=" + key_sn + "&group_sn=" + group_sn

print("11111")
res = urlopen(url_str)
res_string = json.loads((res.read()).decode("utf-8"))
j_res = json.loads(res_string)

status = j_res['status']
print(status)
print(j_res)