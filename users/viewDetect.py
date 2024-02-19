import base64
import datetime
from email.mime import image
from functools import cache
from email.mime import image
import json
from tkinter import Image
from django.shortcuts import redirect, render
import os
import random
import re
from unittest import result
from cachetools import cached
import cv2
import django
import numpy as np
# # from sympy import det
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skindetect.settings')
django.setup()
from django.http import JsonResponse
from rest_framework.decorators import api_view
import torch
from django.utils import timezone
from django.conf import settings
from .models import DetectInfo, SkinDisease
from django.core.files.base import ContentFile
from datetime import datetime
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.cache import cache



name_arr = ['Actinic keratoses',
            'Actinic keratoses',
            'Actinic keratoses',
            'Cell carcinoma',
            'Cell carcinoma',
            'Cell carcinoma',
            'Cell carcinoma',
            'Benign Skin lesions',
            'Benign Skin lesions',
            'Benign Skin lesions',
            'Benign Skin lesions',
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

current_datetime = datetime.now()

def getImage(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')
            return image_file
        except MultiValueDictKeyError:
            print("Image not found in request.FILES")
    return None


def detect(image_file):
    if image_file and image_file.size > 0:

        image_string = image_file.read()
         # image_string = base64.b64decode(image_file)
        jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        print("Length of jpg_as_np:", len(jpg_as_np))
        # original_image = cv2.imdecode(jpg_as_np, flags=1)
        original_image = cv2.imdecode(jpg_as_np, flags=cv2.IMREAD_COLOR)

        shape = original_image.shape
        print(shape)
        image_resize = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        imgs = [image_resize]

        result = model(imgs, size=640)
        return result
    return None


def getDetectResult(result):
    date = current_datetime.strftime("%Y-%m-%d")  # Extract the date
    time = current_datetime.strftime("%H:%M:%S")  # Extract the time 
   
    if result.pandas() is not None:
        print('checkkkk')
        xyxy_values = result.pandas().xyxy[0].values
        if xyxy_values.any():
            score = xyxy_values[0][4]
            id = xyxy_values[0][5]
            name = name_arr[id]
            print(score, id, name)
            # if (score >= float(0.8) and (id <= 17 or id >= 19)):
            return [name, float(score), date, time, id, result]

    score = random.uniform(0.01, 0.1)
    return ["Skin without pathology!.", float(score), date, time, '8']


# @login_required
def saveDetectInfor(user, img, detect_result):
    # print("Type of img:", type(img))
    if user is not None:
        if img is not None:
            data = detect_result
            name = data[0]
            date = data[2]
            time = data[3]
            disease_id = data[4]
            score = data[1]

            detect_date = (date) + "_" + (time).replace(":", "-")

            image_filename = detect_date + '.jpg'
            # image_path = os.path.join(settings.MEDIA_ROOT, 'detect_pics', image_filename)
            print(time)
            print(date)
            print(image_filename)
            try:
                print("Provied disase_id: ", disease_id)
                skin_disease_instance = get_object_or_404(SkinDisease, pk=disease_id)

                # Create a DetectInfo instance
                user_id = user.id
                detect_info = DetectInfo(
                    user_id=user_id,
                    detect_date=current_datetime,
                    disease=skin_disease_instance,
                    detect_score=score,
                    detect_result=name,
                )

                # Attach the image file to the instance
                image_data = img.read()
                detect_info.detect_photo.save(image_filename, ContentFile(image_data), save=False)

                detect_info.save()  # Save the instance to the database

                print("Image and file inserted successfully into DetectInfo table")
            except Exception as e:
                print("Failed inserting data into DetectInfo table: {}".format(e))
    
def detectImage(request):
    if request.method == 'POST':
        user = request.user
        print(user)
        img = getImage(request)
        detect_result = detect(img)
        result = getDetectResult(detect_result)
        saveDetectInfor(user, img, result)   
        return redirect('index')
    else:
        return render(request, 'users/detect.html')  


# detect image function
@api_view(['POST'])
def getimage(request):
    try:
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< DETECT Image >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        image = request.data.get('file')
        # confidence_score = request.data.get('confidence_score')
        user_id = request.data.get('user_id')
        # print("Confidence Score: " + " " + confidence_score + "**************************************\n")
        print('User_id from was received from Mobile: ', user_id)

        image_string = base64.b64decode(image)

        jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        original_image = cv2.imdecode(jpg_as_np, flags=1)

        shape = original_image.shape
        print(shape)
        image_resize = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        imgs = [image_resize]

        results = model(imgs, size=640)

        current_datetime = timezone.localtime(timezone.now())  # Get the current date

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
                data = {}
                if (score >= float(0.8) and (id <= 17 or id >= 19)):
                    data = {
                        'placement': str(name),
                        'score': float(score),
                        'date': date,
                        'time': time,
                        'id': str(id),
                    }
                else:
                    data = {
                        'placement': str(name),
                        'score': float(score),
                        'date': date,
                        'time': time,
                        'id': str(id),
                    }
                storeImageById(image_path, name, user_id, id, score)
                return JsonResponse(data)
            else:
                name = "Skin without pathology!."
                score = random.uniform(0.01, 0.1)
                id = 8
                data = {
                    'placement': str(name),
                    'score': float(score),
                    'date': date,
                    'time': time,
                    'id': str(id),
                }
                print('data', data)
                storeImageById(image_path, name, user_id, id, score)
                return JsonResponse(data)
    except Exception as e:
        name = "Skin without pathology!."
        score = random.uniform(0.01, 0.1)
        id = 8
        user_id = request.data.get('user_id')
        current_datetime = timezone.localtime(timezone.now())  # Get the current date
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = os.path.join(settings.MEDIA_ROOT, 'detect_pics', image_filename)
 
        data = {
            'placement': str(name),
            'score': float(score),
            'date': date,
            'time': time,
            'id': str(id),

        }
        print('data', data)
        storeImageById(image_path, name, user_id, id, score)
        return JsonResponse(data, status=500)
# store image function
def storeImageById(image_path, text_path, user_id, disease_id, image_score):
    try:
        print("<<<<<<<<<<<<<<<<Save Image>>>>>>>>>>>>>>>")

        current_datetime = datetime.now()
        # print('current_datetime:', current_datetime) # Get the current date
        detect_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        print('detect_date:', detect_date)
        print("Provied disase_id: ", disease_id)
        skin_disease_instance = get_object_or_404(SkinDisease, pk=disease_id)

        # Create a DetectInfo instance
        detect_info = DetectInfo(
            user_id=user_id,
            detect_date=current_datetime,
            disease=skin_disease_instance,
            detect_score=image_score           
        )

        # Attach the image and text file to the instance
        # detect_info.detect_photo.save(os.path.basename(image_path), ContentFile(open(image_path, 'rb').read()))
        with open(image_path, 'rb') as f:
            detect_info.detect_photo.save(os.path.basename(image_path), ContentFile(f.read()), save=False)
        # path = 'detect_pics/' + image_path
        # detect_info.detect_photo = path
        detect_info.detect_result = text_path
        detect_info.save()  # Save the instance to the database

        print("Image and file inserted successfully into DetectInfo table")
    except Exception as e:
        print("Failed inserting data into DetectInfo table: {}".format(e))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
# fetch history function
@api_view(['POST'])
def getHistory(request):
    print(">>>>>>>>>>>>>>>>>>History<<<<<<<<<<<<<<<<")
    user_id = request.data.get('user_id')
    print("User_id", user_id)

    cache_key = f'history_{user_id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        print('cache hit')
        return JsonResponse(cached_data)
    try:
        # Query the database using Django ORM
        records = DetectInfo.objects.filter(user_id=user_id).order_by('-detect_date')
        results = []
        for row in records:
            detect_photo_base64 = base64.b64encode(row.detect_photo.read()).decode('utf-8')
            result = {
                'detect_id': row.detect_id,
                'user_id': getattr(row, 'user_id', None),
                'detect_date': row.detect_date,
                'detect_photo': detect_photo_base64,
                'detect_result': row.detect_result,
                'disease_id': row.disease.disease_id,
                'detect_score': float(row.detect_score)
            }           
            results.append(result)
        record_count = len(results)
        print(record_count)
        json_data  = json.dumps(results, default=json_serial)
        jsonData = { 'placement': json_data}
        cache.set(cache_key, jsonData)
        print("Load successful")
        return JsonResponse(jsonData)

    except Exception as error:
        print(f"Error while executing the query: {error}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
# delete image function
@api_view(['POST'])
def deleteImage(request):
    result = -1
    try:
        print("<<<<<<<<<<<<<<<<DeleteImage>>>>>>>>>>>>>>>")

        detect_id = request.data.get('detect_id')
        user_id = request.data.get('user_id')

        with connection.cursor() as cursor:
            query = """
                    DELETE FROM users_detectinfo
                    WHERE user_id = %s AND detect_id = %s
                """
            values = (user_id, detect_id)
            cursor.execute(query, values)

        result = 0
        result_data = {'placement': int(result)}
        print("Delete Successfully")
        return JsonResponse(result_data)

    except Exception as e:
        result = 1
        result_data = {'placement': int(result)}
        print("Delete Unsuccessfully: {}".format(e))
        return JsonResponse(result_data)
# fetch disease detail function
@api_view(['POST'])
def getDetail(request):
    print(">>>>>>>>>>>>>>>>>>Disease Detail<<<<<<<<<<<<<<<<")
    disease_id = request.data.get('diseasedId')
    print("Disease_id", disease_id)
    disese = get_object_or_404(SkinDisease, pk=disease_id)

    #load image from folder
    image_folder = disese.disease_images_folder
    image_paths = []
    if image_folder:
        folder_path = os.path.join(settings.MEDIA_ROOT,'disease_pics/', image_folder)
        for i in range(1, 10):
            image_path = os.path.join(folder_path, f'image{i}.jpg')
            if os.path.isfile(image_path):
                image_paths.append(image_path)
    image_urls = [base64.b64encode(open(image_path, 'rb').read()).decode('utf-8') for image_path in image_paths]
    disease_model = {
        'diseased_Id': disese.disease_id,
        'diseased_name': disese.disease_name,
        'diseased_overview': disese.disease_overview,
        'diseased_symptom': disese.disease_symptoms,
        'diseased_causes': disese.disease_causeses,
        'diseased_prevention': disese.disease_preventions,
        'diseased_image_folder': image_urls,
    }
    jsonData = { 'diseaseModel': disease_model}
    return JsonResponse(jsonData)

@api_view(['GET'])
def getListDetail(request):
    print(">>>>>>>>>>>>>>>>>>List Detail<<<<<<<<<<<<<<<<")
    jsonData = { 'placement': None}
    disease_ids = [1,4,8,12,14,18,21]
    results = []
    for disease_id in disease_ids:        
        diseases = SkinDisease.objects.filter(disease_id__in=[disease_id])
        for disease in diseases:
            #load image from folder
            image_folder = disease.disease_images_folder
            image_paths = []
            if image_folder:
                folder_path = os.path.join(settings.MEDIA_ROOT,'disease_pics/', image_folder)
                for i in range(1, 10):
                    image_path = os.path.join(folder_path, f'image{i}.jpg')
                    if os.path.isfile(image_path):
                        image_paths.append(image_path)
            image_urls = [base64.b64encode(open(image_path, 'rb').read()).decode('utf-8') for image_path in image_paths]
            # print('image_urls', image_urls)
            disease_model = {
                'diseased_Id': disease.disease_id,
                'diseased_name': disease.disease_name,
                'diseased_overview': disease.disease_overview,
                'diseased_symptom': disease.disease_symptoms,
                'diseased_causes': disease.disease_causeses,
                'diseased_prevention': disease.disease_preventions,
                'diseased_image_folder': image_urls,                  
            }
            results.append(disease_model)      
    record_count = len(results)
    print("record_count",record_count)
    json_data = json.dumps(results, default=json_serial)
    jsonData = { 'placement': json_data}
    return JsonResponse(jsonData)
        