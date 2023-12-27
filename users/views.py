import base64
import datetime
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
from users.models import Profile
from django.core.files.base import ContentFile
import base64
import base64
import torch


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

def index(request):
    return render(request, 'users/index.html')
def register(request):
    if request.method == 'POST':
        if (request.POST['password1'])== (request.POST['password2']):
            try:
               User.objects.get(username = request.POST['username'])
               return render(request,'users/register.html', {'error':'Username is already exist!'})
            except User.DoesNotExist:
               user = User.objects.create_user(request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
               auth.login(request,user)
               return redirect('index')
        else:
            return render (request,'users/register.html', {'error':'Password does not match!'})
    else:
       return render(request, 'users/register.html')
    

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request,user)
            return redirect('index')
        else:
            return render(request,'users/login.html', {'error':'Username or password is incorrect!'})
    else:
        return render(request, 'users/login.html')
    

def logout(request):
    auth.logout(request)
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        try:
            profile = Profile(user=user)
            profile.save()
        except FileNotFoundError:
            # Handle the case where the 'default.jpg' file is not found
            # Provide a default image path or handle this differently
            profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
           # Get the avatar file from the form
            avatar_file = form.cleaned_data['avatar']

            # Check if a new avatar file was provided
            if avatar_file:
                # Rename the avatar file based on user ID
                user_id = user.id
                filename = f"{user.id}_{str(uuid.uuid4())[:8]}_{avatar_file.name}"
                profile.avatar.save(filename, avatar_file)
            form.save()
            return redirect('profile') 
    else:
        # Pass the user data to the form when instantiating it
        form = ProfileForm(instance=profile, initial={'first_name': user.first_name, 'last_name': user.last_name})


    return render(request, 'users/view_profile.html', {'user': user, 'profile': profile, 'form': form})

# @api_view(['POST'])
# def loginMobileTest(request):
#     print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Login >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#     result = {'placement': -1, 'user': None, 'message': ''}

#     if request.method == 'POST':
#         user = auth.authenticate(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'])
#         if user is not None:
#             auth.login(request,user)
#         else:
#             result['placement'] = 1
#             result['message'] = 'Incorrect username / password!'
#         print('-------------------------------')
#         print(result['message'])
#         print('-------------------------------')
#         print('Email: ' + request.POST['email'] + "\n", 'Username:' + request.POST['username'] + "\n")

#     return JsonResponse(result)

@api_view(['POST'])
def profileMobile(request):
    user = request.user
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        try:
            profile = Profile(user=user)
            profile.save()
        except FileNotFoundError:
            # Handle the case where the 'default.jpg' file is not found
            # Provide a default image path or handle this differently
            profile = Profile(user=user)
    if request.method == 'POST':
        


# @require_POST
@api_view(['POST'])
def loginMobile(request):
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Login >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    result = {'placement': -1, 'user': None, 'message': ''}

    if 'email' in request.POST and 'password' in request.POST:
        print("Thong bao login qua duoc")
        # Fetch form data
        email = request.POST['email'] or request.POST['username']
        password = request.POST['password']

        # Custom authentication function
        user = auth.authenticate(username=email, password=password)
        if user:
            auth.login(request, user)
 
            try:
                profile = Profile.objects.get(user=user)

                result['message'] = 'Logged in successfully!'
                result['placement'] = 0
                result['user'] = {
                    'user_id': getattr(user, 'id', None),
                    'user_name': user.get_username(),
                    'user_email': getattr(user, 'email', None),
                    'user_avatar': base64.b64encode(profile.user_avatar).decode('utf-8') if profile.user_avatar else None,
                    'user_phone': profile.user_phone if profile else None,
                    'user_address': profile.user_address if profile else None,
                    # Add other fields as needed
                }
            except Profile.DoesNotExist:
                result['placement'] = 1
                result['message'] = 'Profile not found for the user.'

        else:
            result['placement'] = 1
            result['message'] = 'Incorrect username / password!'
        print('-------------------------------')
        print(result['message'])
        print('-------------------------------')
        print('Email: ' + email + "\n", 'Password: ' + password + "\n")

    return JsonResponse(result)

@api_view(['POST'])
def registerMobile(request):
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Register >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    result = {'placement': -1, 'message': ''}

    if 'email' in request.POST and 'password' in request.POST and 'user_name' in request.POST:
        print("Thong bao register qua duoc")
        # Fetch form data
        email = request.POST['email'] 
        password = request.POST['password']
        username = request.POST['user_name']
        # print(email)
        # print(username)
        try:
            User.objects.get(email = request.POST['email'])
            result['placement'] = 1
            result['message'] = 'Email already exist!'
            print('-------------------------------')
            print(result['message'])
            print('-------------------------------')
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password, email=email)
            auth.login(request, user)
            #Profile.objects.create(user=user, gender='', user_address='', user_phone='', user_dob=None, user_avatar=None)
            result['placement'] = 0
            result['message'] = 'Register successfully!'
            print('-------------------------------')
            print(result['message'])
            print('-------------------------------')
            print('Email: ' + email + "\n", 'Password: ' + password + "\n")
    return JsonResponse(result)


@api_view(['POST'])
def updateMobile(request):
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Update >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    if (
        request.method == 'POST'
        and 'email' in request.data
        and 'user_name' in request.data
        # and 'password' in request.data
        and 'user_address' in request.data
        and 'user_phone' in request.data
        and 'user_dob' in request.data
    ):
        print("thong bao da qua duoc")
        user_data = request.data
        email = user_data['email']
        # password = user_data['password']
        user_name = user_data['user_name']
        user_address = user_data['user_address']
        user_phone = user_data['user_phone']
        user_dob = user_data['user_dob']
        user_id = user_data['user_id']
        user_avatar = request.data.get('user_avatar')  # Assuming 'user_avatar' is a file field
        from datetime import datetime
        # Decode the image after receiving
        image_string = base64.b64decode(user_avatar)
        jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        original_image = cv2.imdecode(jpg_as_np, flags=1)

        # Resize the image to a specific width and height
        new_width, new_height = 300, 300
        original_image_resize = cv2.resize(original_image, (new_width, new_height))

        current_datetime = datetime.now()

        # Create the path to save the avatar
        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = f'/Users/hachicao/File Image and Json Caoproject/avatar/{image_filename}'
        # Save the image to the specified path
        cv2.imwrite(image_path, original_image_resize)
        print("Avatar was saved to File Image and Json Caoproject Folder")

        # Convert picture to Binary before saving to the Db
        avatar_picture = convert_to_binary_data(image_path)

        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        user.username = user_name
        user.email = email
        profile.user_address = user_address
        profile.user_phone = user_phone
        profile.user_dob = user_dob
        profile.user_avatar = avatar_picture
        profile.save()
        user.save()

        result = {'placement': 0, 'message': 'Update Successfully'}
        print('-------------------------------')
        print(result['message'])
        print('-------------------------------')

        return JsonResponse(result)
    else:
        result = {'placement': 1, 'message': 'Update Failed'}
        print('-------------------------------')
        print(result['message'])
        print('-------------------------------')
        return JsonResponse(result)

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

@api_view(['POST'])
def getimage(request):
    try:
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< DETECT Image >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        image = request.form.get('file')
        confidence_score = request.form.get('confidence_score')
        user_id = request.form.get('user_id')
        print("Confidence Score: " + " " + confidence_score + "**************************************\n")
        print('User_id from was received from Mobile: ', user_id)

        image_string = base64.b64decode(image)

        jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        original_image = cv2.imdecode(jpg_as_np, flags=1)

        shape = original_image.shape
        print(shape)
        image_resize = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        imgs = [image_resize]
        from datetime import datetime

        results = model(imgs, size=640)

        current_datetime = datetime.now()

        date = current_datetime.strftime("%Y-%m-%d")  # Extract the date
        time = current_datetime.strftime("%H:%M:%S")  # Extract the time

        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = r'/Users/hachicao/File Image and Json Caoproject/photo/{}'.format(image_filename)
        # Save the image to the specified path
        cv2.imwrite(image_path, original_image)
        print("Image was saved to File Image and Json Caoproject Folder")
        if user_id == 'null':
            # Handle the case when user_id is None (null)
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
                return data
        else:
            if results.pandas() is not None:
                # xmin = results.pandas().xyxy[0].values[0][0]
                # ymin = results.pandas().xyxy[0].values[0][1]
                # xmax = results.pandas().xyxy[0].values[0][2]
                # ymax = results.pandas().xyxy[0].values[0][3]
                score = results.pandas().xyxy[0].values[0][4]
                id = results.pandas().xyxy[0].values[0][5]
                # name = results.pandas().xyxy[0].values[0][6]
                name = name_arr[id]
                print(score, id, name)
                text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
                txt_path = r'/Users/hachicao/File Image and Json Caoproject/text/{}'.format(text_filename)
                with open(txt_path, 'w') as file:
                    file.write(name)
                data = {}
                if (score >= float(0.8) and (id <= 17 or id >= 19)):
                    data = {
                        'placement': str(name),
                        # 'ymin': str(abs(ymin)),
                        # 'xmin': str(abs(xmin)),
                        # 'ymax': str(abs(ymax)),
                        # 'xmax': str(abs(xmax)),
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
                # storeImageById(image_path, txt_path, user_id, id, score)
                return data
            else:
                name = "Skin without pathology!."
                score = random.uniform(0.01, 0.1)
                id = 8
                text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
                txt_path = r'/Users/hachicao/File Image and Json Caoproject/text/{}'.format(text_filename)
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
                # json_data = json.dumps(data)
                print('data', data)
                # storeImageById(image_path, txt_path, user_id, id, score)
                return data
    except Exception as e:
        name = "Skin without pathology!."
        score = random.uniform(0.01, 0.1)
        id = 8
        from datetime import datetime
        current_datetime = datetime.now()
        date = current_datetime.strftime("%Y-%m-%d")  # Extract the date
        time = current_datetime.strftime("%H:%M:%S")
        text_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
        txt_path = r'/Users/hachicao/File Image and Json Caoproject/text/{}'.format(text_filename)
        image_filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
        image_path = r'/Users/hachicao/File Image and Json Caoproject/photo/{}'.format(image_filename)
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
        # storeImageById(image_path, txt_path, user_id, id, score)
        return data, 500
        print(f"An error occurred: {str(e)}")


from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
# from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
import uuid
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
# from users.forms import (EditProfileForm, ProfileForm)

# Create your views here.
def index(request):
    return render(request, 'users/index.html')

def register(request):
    if request.method == 'POST':
        if (request.POST['password1'])== (request.POST['password2']):
            try:
               User.objects.get(username = request.POST['username'])
               return render(request,'users/register.html', {'error':'Username is already exist!'})
            except User.DoesNotExist:
               user = User.objects.create_user(request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
            #    Profile(user=user, dob=None, gender=None)
               auth.login(request,user)
               return redirect('index')
        else:
            return render (request,'users/register.html', {'error':'Password does not match!'})
    else:
       return render(request, 'users/register.html')
    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')  # Make sure you have an 'index' URL pattern
        else:
            return render(request, 'users/login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'users/login.html')
    

def logout(request):
    auth.logout(request)
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        try:
            profile = Profile(user=user)
            profile.save()
        except FileNotFoundError:
            # Handle the case where the 'default.jpg' file is not found
            # Provide a default image path or handle this differently
            profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
           # Get the avatar file from the form
            avatar_file = form.cleaned_data['avatar']

            # Check if a new avatar file was provided
            if avatar_file:
                # Rename the avatar file based on user ID
                user_id = user.id
                filename = f"{user.id}_{str(uuid.uuid4())[:8]}_{avatar_file.name}"
                profile.avatar.save(filename, avatar_file)
            form.save()
            return redirect('profile') 
    else:
        # Pass the user data to the form when instantiating it
        form = ProfileForm(instance=profile, initial={'first_name': user.first_name, 'last_name': user.last_name})


    return render(request, 'users/view_profile.html', {'user': user, 'profile': profile, 'form': form})