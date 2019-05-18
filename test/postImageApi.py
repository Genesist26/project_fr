import os
import requests


def post_image(filepath):
    files = {
        'file': ('image.jpg', open(filepath, 'rb'), '.jpg'),
    }

    response = requests.post('http://localhost/code2/news/stream', files=files)
    print(response.status_code)
    print(response.json())


dirname = os.path.dirname(__file__)
filepath = dirname + '/image.jpg'
post_image(filepath)
