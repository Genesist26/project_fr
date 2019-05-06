import requests
r = requests.post('http://httpbin.org/post', json={"key": "value"})
print(r.status_code)
print(r.json())