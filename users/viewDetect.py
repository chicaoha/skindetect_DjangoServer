import base64
import datetime
import json
import os
import random
from unittest import result
import cv2
import django
import numpy as np
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
# detect image function
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
                storeImageById(image_path, txt_path, user_id, id, score)
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
                storeImageById(image_path, txt_path, user_id, id, score)
                return JsonResponse(data)
    except Exception as e:
        name = "Skin without pathology!."
        score = random.uniform(0.01, 0.1)
        id = 8
        user_id = request.data.get('user_id')
        current_datetime = timezone.now()
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
        txt_path = os.path.join(settings.MEDIA_ROOT, 'detect_text', text_filename)
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
        storeImageById(image_path, txt_path, user_id, id, score)
        return JsonResponse(data, status=500)
# store image function
def storeImageById(image_path, text_path, user_id, disease_id, image_score):
    try:
        print("<<<<<<<<<<<<<<<<Save Image>>>>>>>>>>>>>>>")

        current_datetime = timezone.now()
        detect_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        print("Provied disase_id: ", disease_id)
        skin_disease_instance = get_object_or_404(SkinDisease, pk=disease_id)

        # Create a DetectInfo instance
        detect_info = DetectInfo(
            user_id=user_id,
            detect_date=detect_date,
            disease=skin_disease_instance,
            detect_score=image_score
        )

        # Attach the image and text file to the instance
        detect_info.detect_photo.save('detect_photo.jpg', ContentFile(open(image_path, 'rb').read()))
        detect_info.detect_result.save('detect_result.txt', ContentFile(open(text_path, 'r').read()))

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
        
        # Add the missing import statement

        results = []
        for row in records:
            detect_photo_base64 = base64.b64encode(row.detect_photo.read()).decode('utf-8')
            detect_result_content = row.detect_result.read().decode('utf-8')  # Decode bytes to string
            result = {
                'detect_id': row.detect_id,
                'user_id': getattr(row, 'user_id', None),
                'detect_date': row.detect_date,
                'detect_photo': detect_photo_base64,
                'detect_result': detect_result_content,
                'disease_id': row.disease.disease_id,
                'detect_score': float(row.detect_score)
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
    disease_model = {
        'diseased_Id': disese.disease_id,
        'diseased_name': disese.disease_name,
        'diseased_overview': disese.disease_overview,
        'diseased_symptom': disese.disease_symptoms,
        'diseased_causes': disese.disease_causeses,
        'diseased_prevention': disese.disease_preventions,
        'diseased_photo_1': base64.b64encode(disese.disease_image1.read()).decode('utf-8'),
        'diseased_photo_2': base64.b64encode(disese.disease_image2.read()).decode('utf-8'),
        'diseased_photo_3': base64.b64encode(disese.disease_image3.read()).decode('utf-8'),
        'diseased_photo_4': base64.b64encode(disese.disease_image4.read()).decode('utf-8'),
        # 'diseased_photo_5': base64.b64encode(disese.disease_image5.read()).decode('utf-8'),
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
            disease_model = {
                'diseased_Id': disease.disease_id,
                'diseased_name': disease.disease_name,
                'diseased_overview': disease.disease_overview,
                'diseased_symptom': disease.disease_symptoms,
                'diseased_causes': disease.disease_causeses,
                'diseased_prevention': disease.disease_preventions,        
                'diseased_photo_1': base64.b64encode(disease.disease_image1.read()).decode('utf-8'),
                'diseased_photo_2': base64.b64encode(disease.disease_image2.read()).decode('utf-8'),
                'diseased_photo_3': base64.b64encode(disease.disease_image3.read()).decode('utf-8'),
                'diseased_photo_4': base64.b64encode(disease.disease_image4.read()).decode('utf-8'),
                # 'diseased_photo_5': base64.b64encode(disease.disease_image5.read()).decode('utf-8'),
            }
            results.append(disease_model)      
    record_count = len(results)
    print("record_count",record_count)
    json_data = json.dumps(results, default=json_serial)
    jsonData = { 'placement': json_data}
    return JsonResponse(jsonData)
        