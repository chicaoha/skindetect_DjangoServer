import base64
import datetime
import os
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

# @login_required
def profile(request):
        
    # if request.method == 'POST':
        # form = EditProfileForm(request.POST, instance=request.user)
        # profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.userprofile)  # request.FILES is show the selected image or file

        # if form.is_valid() and profile_form.is_valid():
        #     user_form = form.save()
        #     custom_form = profile_form.save(False)
        #     custom_form.user = user_form
        #     custom_form.save()  
            # return redirect('accounts:view_profile')
    # else:
        # form = EditProfileForm(instance=request.user)
        # profile_form = ProfileForm(instance=request.user.userprofile)
        args = {}
        # args.update(csrf(request))
        # args['form'] = form
        # args['profile_form'] = profile_form
    # return render(request, 'users/profile.html')




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
            Profile.objects.create(user=user, gender='', user_address='', user_phone='', user_dob=None, user_avatar=None)
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

