import requests

files = {
    'form': ('images.jpg',open('images.jpg', 'rb'),'image/jpg'),
}

response = requests.post('http://localhost:5000/face/v1.0/detect?returnFaceId=true&returnFaceLandmarks=false', files=files)
print(response.json())