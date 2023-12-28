import base64
import datetime
import io
import os
import random
import cv2
import django
from cProfile import Profile
from imaplib import _Authenticator
from multiprocessing import connection
import MySQLdb
import numpy as np
from sympy import use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skindetect.settings')
django.setup()
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from requests import request
from django.views.decorators.http import require_POST
from django.db import connection
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
import base64
import base64
import torch
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
import os


name_arr = ['Actinic keratoses',
            'Actinic keratoses',
            'Actinic keratoses',
            'Cell carcinoma',
            'Cell carcinoma',
            'Cell carcinoma',
            'Cell carcinoma',
            'Benign lesions',
            'Benign lesions',
            'Benign lesions',
            'Benign lesions',
            'Dermatofibroma',
            'Dermatofibroma',
            'Melanoma',
            'Melanoma back',
            'Melanoma lower',
            'Melanoma upper',
            'Melanocytic nevi',
            'Melanocytic nevi',
            'Melanocytic nevi',
            'Vascular lesions',
            'Vascular lesions',
            'Vascular lesions',
            'Vascular lesions']
model = torch.hub.load('ultralytics/yolov5', 'custom', path='08_12_22_noon_best.pt', force_reload=True)

@api_view(['POST'])
def getimage(request):
    try:
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< DETECT Image >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        image = request.data.get('file')
        confidence_score = request.data.get('confidence_score')
        user_id = request.data.get('user_id')
        print("Confidence Score: " + " " + confidence_score + "**************************************\n")
        print('User_id from was received from Mobile: ', user_id)

        image_string = base64.b64decode(image)

        jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        original_image = cv2.imdecode(jpg_as_np, flags=1)

        shape = original_image.shape
        print(shape)
        image_resize = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        imgs = [image_resize]

        results = model(imgs, size=640)

        current_datetime = timezone.now()

        date = current_datetime.strftime("%Y-%m-%d")  # Extract the date
        time = current_datetime.strftime("%H:%M:%S")  # Extract the time

        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = os.path.join(settings.MEDIA_ROOT, 'detect_pics', image_filename)
        # Save the image to the specified path
        cv2.imwrite(image_path, original_image)
        # print("Image was saved to File Image and Json Caoproject Folder")

        if user_id == 'null':
            if results.pandas() is not None:
                score = results.pandas().xyxy[0].values[0][4]
                id = results.pandas().xyxy[0].values[0][5]
                name = name_arr[id]
                print(score, id, name)
                data = {}
                if (score >= float(0.8) and (id <= 17 or id >= 19)):
                    data = {
                        'placement': str(name),
                        'score': float(score),
                        'date': date,
                        'time': time,
                        'id': str(id),
                    }
                return JsonResponse(data)
        else:
            if results.pandas() is not None:
                score = results.pandas().xyxy[0].values[0][4]
                id = results.pandas().xyxy[0].values[0][5]
                name = name_arr[id]
                print(score, id, name)
                text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
                txt_path = os.path.join(settings.MEDIA_ROOT, 'detect_text', text_filename)
                with open(txt_path, 'w') as file:
                    file.write(name)
                data = {}
                if (score >= float(0.8) and (id <= 17 or id >= 19)):
                    data = {
                        'placement': str(name),
                        'score': float(score),
                        'date': date,
                        'time': time,
                        'id': str(id),
                        'image_path': image_path,
                        'txt_path': txt_path
                    }
                else:
                    data = {
                        'placement': str(name),
                        'score': float(score),
                        'date': date,
                        'time': time,
                        'id': str(id),
                        'image_path': image_path,
                        'txt_path': txt_path
                    }
                return JsonResponse(data)
            else:
                name = "Skin without pathology!."
                score = random.uniform(0.01, 0.1)
                id = 8
                text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
                txt_path = os.path.join(settings.MEDIA_ROOT, 'detect_text',  text_filename)
                with open(txt_path, 'w') as file:
                    file.write(name)
                data = {
                    'placement': str(name),
                    'score': float(score),
                    'date': date,
                    'time': time,
                    'id': str(id),
                    'image_path': image_path,
                    'txt_path': txt_path
                }
                print('data', data)
                return JsonResponse(data)
    except Exception as e:
        name = "Skin without pathology!."
        score = random.uniform(0.01, 0.1)
        id = 8
        current_datetime = timezone.now()
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
        txt_path = os.path.join(settings.MEDIA_ROOT, 'detect_pics', 'text', text_filename)
        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = os.path.join(settings.MEDIA_ROOT, 'detect_pics', image_filename)
        with open(txt_path, 'w') as file:
            file.write(name)
        data = {
            'placement': str(name),
            'score': float(score),
            'date': date,
            'time': time,
            'id': str(id),
            'image_path': image_path,
            'txt_path': txt_path
        }
        print('data', data)
        return JsonResponse(data, status=500)

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data
