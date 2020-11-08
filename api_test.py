import requests
import numpy as np
import matplotlib.pyplot as plt
import cv2
import json
from PIL import Image, ImageDraw
import io
import jwt

URL = 'http://localhost:8189/colorize'
SECRET_KEY = b'_5#y2L"F4%Q6@TFH1*876$tgfdegh001lq.s!#2115#8z\n\xec]/'
ACCESS_KEY = b"\xf9'\xe4p(\xa9\x12\x1a!\x94\x8d\x1c\x99l\xc7\xb7e\xc7c\x86\x02MJ\xa0"

with open('static/images/places/Places365_val_00014395.jpg', 'rb') as file: # cv2 reads in BGR
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = {'img': file}
    header = {'ACCESS_KEY': ACCESS_KEY}
    # print(f'IMG SHAPE FROM REQUEST: {image.shape}')
    r = requests.post(URL, files=data, headers=header)
    print('Posted image...')

    print(f'Status code: {r.status_code}')
    if r.status_code == requests.codes.ok:
        stream = io.BytesIO(r.content)
        img = Image.open(stream)
        draw = ImageDraw.Draw(img)

        nparray = np.asarray(img, dtype='uint8')
        # print(f'Array: {nparray}')
        plt.imshow(nparray)
        plt.show()