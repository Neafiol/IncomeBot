import json

import requests


def uploadphot(image):
    files = {'image': image}

    headers = {'Authorization': "TOKEN " + 'aygXDbL1fwuPqs2C9B0i'}
    r = requests.post("https://api.imageban.ru/v1", headers=headers, files=files)

    print(json.loads(r.content.decode('utf-8'))["data"]["link"])