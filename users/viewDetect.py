import base64
import datetime
from email.mime import image
import json
import time
from tkinter import Image
from django.forms import ValidationError
from django.shortcuts import redirect, render
import os
import random
import re
from unittest import result
import cv2
import django
import numpy as np
from tarfile import TarFile

from django.core.paginator import Paginator
from users.forms import DetectInfoForm
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skindetect.settings')
django.setup()
from django.http import JsonResponse
from rest_framework.decorators import api_view
import torch
from django.utils import timezone
from django.conf import settings
from .models import DetectInfo, SkinDisease
from django.core.files.base import ContentFile
from datetime import date, datetime
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist



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
model = torch.hub.load('ultralytics/yolov5', 'custom', path='08_12_22_noon_best.pt')
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')

current_datetime = datetime.now()

def getImage(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES['detect_photo']
            return image_file
        except MultiValueDictKeyError:
            print("Image not found in request.FILES")
    return None

def detect(image_file):
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    if image_file and image_file.size > 0:
        try:
            image_string = image_file.read()
            jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
            # print("Length of jpg_as_np:", len(jpg_as_np))
            original_image = cv2.imdecode(jpg_as_np, flags=cv2.IMREAD_COLOR)

            shape = original_image.shape
            # print(shape)
            image_resize = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            imgs = [image_resize]

            result = model(imgs, size=640)

            if result and result.pandas() is not None:
                xyxy_values = result.pandas().xyxy[0].values
                if xyxy_values.any():
                    score = xyxy_values[0][4]
                    id = xyxy_values[0][5]
                    name = name_arr[id]
                    # print('checkkkk')
                    print(score, id, name)
                    return [name, float(score), date, time, id+1, result]
            score = random.uniform(0.01, 0.1)
            return ["Skin without pathology!", float(score), date, time, '8']
        except cv2.error as e:
            print("Error in image decoding: {}".format(e))
        except Exception as e:
            print("An unexpected error occurred: {}".format(e))
    score = random.uniform(0.01, 0.1)
    return ["Skin without pathology!", float(score), date, time, '8']

def showResult(request):
    detect_id = request.session.pop('detect_id', None)

    if detect_id is not None:
        # Use get_object_or_404 to get a single instance or raise a 404 error
        detect_info = get_object_or_404(DetectInfo, detect_id=detect_id)
        return render(request, 'users/detect_result.html', {'detect_info': detect_info})
    else:
        return render(request, 'users/detect.html')


def history(request):
    user = request.user
    if user is not None:
        data_filter = DetectInfo.objects.filter(user_id=user.id)
        for data in data_filter:
            if data.detect_score is not None:
                data.detect_score = round(data.detect_score * 100)

        # Implement pagination logic
        objects_per_page = 10
        paginator = Paginator(data_filter, objects_per_page)
        page_number = request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        return render(request, 'users/detect_history.html', {'page_objects': page_objects})
    return render(request, 'users/detect_history.html', {'page_objects': None})


import os
from django.conf import settings

import os
from django.conf import settings

def aboutDisease(request):
    d_id = request.GET.get('id')
    skin_disease = None
    image_filenames = []
    image_folder_path = None  # Initialize image_folder_path

    if d_id is not None:
        skin_disease = SkinDisease.objects.filter(disease_id=d_id).first()  # Get the first object or None
        if skin_disease:
            image_folder_path = os.path.join(settings.MEDIA_ROOT, 'disease_pics', skin_disease.disease_images_folder) # type: ignore
            if os.path.exists(image_folder_path) and os.path.isdir(image_folder_path):
                image_filenames = [os.path.join('/media', 'disease_pics', skin_disease.disease_images_folder, f) for f in os.listdir(image_folder_path) if os.path.isfile(os.path.join(image_folder_path, f))] # type: ignore

    print("Skin Disease:", skin_disease)
    print("Image Folder Path:", image_folder_path)
    print("Image Filenames:", image_filenames)

    return render(request, 'users/about_disease.html', {'skin_disease': skin_disease, 'image_filenames': image_filenames})


def deleteDetectResult(request):
    detect_id = request.GET.get('detect_id')  # Retrieve detect_id from query parameters
    result = 'unsuccessful'
    if detect_id is not None:
        try:
            query = DetectInfo.objects.get(pk=detect_id)  # Retrieve DetectInfo object with the given detect_id
            query.delete()  # Delete the object
            result = 'successful'
            return render(request, 'users/detect_history.html')
        except DetectInfo.DoesNotExist:
            pass 
    
    return redirect('detectHistory')  # Redirect to the detection history page


@login_required(login_url='login')  
def detectImage(request):
    if request.method == 'POST':
        user = request.user

        if not user.is_authenticated:
            print("User is not authenticated.")
            return render(request, 'users/detect.html', {'form_errors': ['User is not authenticated.']})

        form = DetectInfoForm(request.POST, request.FILES)

        if form.is_valid():
            img = form.cleaned_data['detect_photo']
            result = detect(img)
            date = result[2]
            time = result[3]
            detect_date = (date) + "_" + (time).replace(":", "-")
            formatted_datetime = datetime.strptime(detect_date, "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d %H:%M:%S")
            image_filename = detect_date + '.jpg'

            try:
                # Retrieve the SkinDisease instance based on the ID
                skin_disease_instance = SkinDisease.objects.get(pk=result[4])
            except SkinDisease.DoesNotExist:
                print("Skin Disease with ID {} does not exist.".format(result[4]))
                return render(request, 'users/detect.html', {'form_errors': ['Invalid Skin Disease ID.']})

            detect_info = form.save(commit=False)
            detect_info.user = user
            detect_info.detect_date = formatted_datetime
            detect_info.disease = skin_disease_instance
            detect_info.detect_score = result[1]
            detect_info.detect_result = result[0]
            detect_info.detect_photo.name = image_filename
            detect_info.save()

            print("Image and file inserted successfully into DetectInfo table")
           
            request.session['detect_id'] = detect_info.detect_id
            return redirect('showResult')
        else:
            print("Form is not valid. Errors: {}".format(form.errors))
            return render(request, 'users/detect.html', {'form_errors': form.errors})

    return render(request, 'users/detect.html', {'form': DetectInfoForm()})



# --------------------------------Mobile API--------------------------------#
# 
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
                # if (score >= float(0.8) and (id <= 17 or id >= 19)):
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
                storeImageById(image_path, name, user_id, id, score)
                return JsonResponse(data)
    except Exception as e:
        name = "Skin without pathology!."
        score = random.uniform(0.01, 0.1)
        id = 8
        user_id = request.data.get('user_id')
        current_datetime = timezone.localtime(timezone.now())  # Get the current date
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
        with open(image_path, 'rb') as f:
            detect_info.detect_photo.save(os.path.basename(image_path), ContentFile(f.read()), save=False)
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
                'disease_id': row.disease.disease_id if row.disease else None,
                'detect_score': float(row.detect_score) if row.detect_score is not None else 0.0
            }           
            results.append(result)
        record_count = len(results)
        print(record_count)
        json_data  = json.dumps(results, default=json_serial)
        jsonData = { 'placement': json_data}
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
