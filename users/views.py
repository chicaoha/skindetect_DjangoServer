import base64
from io import BytesIO
import json
import os
import django
from requests import get
# from sympy import use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skindetect.settings')
django.setup()
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile

from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Profile
from .forms import ProfileForm
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from google.auth.transport import requests
from google.auth.transport.requests import Request
from allauth.socialaccount.models import SocialAccount
from django.core.files import File
import requests


# Create your views here.
def index(request):
    return render(request, 'users/phat_index.html')

def about(request):
    return render(request, 'users/about.html')

def forgotPassword(request):
    return render(request, 'users/forgotPassword.html')

def FAQ(request):
    return render(request, 'users/FAQ.html')

def contact(request):
    return render(request, 'users/contact.html')

def blog1(request):
    return render(request, 'users/blog1.html')

def blog2(request):
    return render(request, 'users/blog2.html')

def blog3(request):
    return render(request, 'users/blog3.html')

def article1(request):
    return render(request, 'users/article1.html')

def profilePage(request):
    return render(request, 'users/profilePage.html')

def page404(request):
    return render(request, 'users/page404.html')

# def detect(request):
#     return render(request, 'users/detect.html')

def mobileApp(request):
    return render(request, 'users/mobileApp.html')

# def some_view(request):
#     return render(request, 'users/base.html', {'include_footer': include_footer})

def register(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'users/register.html', {'error': 'Username is already exist!'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'], email=request.POST['email'])

                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('')
        else:
            return render(request, 'users/phat_register.html', {'error': 'Password does not match!'})
    else:
        return render(request, 'users/phat_register.html')

    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('')  
        else:
            return render(request, 'users/phat_log.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'users/phat_log.html')
    

def logout(request):
    auth.logout(request)
    return redirect('')


@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        # If profile doesn't exist, create one
        profile = Profile.objects.create(user=user)
        # Set the default avatar path
        # default_avatar_path = 'profile_pics/default.jpg'
        # profile.avatar.name = default_avatar_path
        
        profile.save()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Check if the 'avatar' field has changed
            if 'avatar' in form.changed_data:
                # Rest of your profile update logic for avatar...
                avatar_file = form.cleaned_data['avatar']

                # Handle the avatar update logic...
                if profile.avatar and profile.avatar.name:
                    old_avatar_path = profile.avatar.path

                    # Save the new avatar file, rename it based on user ID
                    user_id = getattr(profile.user, 'id', None)
                    if user_id:
                        filename = 'avatar.jpg'
                        profile.avatar.name = filename

                        # Ensure the folder path exists
                        # folder_path = os.path.join('media', 'profile_pics', str(user_id))
                        # os.makedirs(folder_path, exist_ok=True)

                        # Save the new avatar file before deleting the old one
                        profile.avatar.save(filename, avatar_file)

                        # Delete the old avatar file
                        if os.path.exists(old_avatar_path):
                            os.remove(old_avatar_path)
                            print(f"Successfully deleted old avatar file at path: {old_avatar_path}")

        form.save()
        return redirect('profilePage')

    else:
        form = ProfileForm(instance=profile, initial={'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

    return render(request, 'users/profilePage.html', {'user': user, 'profile': profile, 'form': form})


# --------------------------------Mobile API--------------------------------#
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
                    'user_avatar': base64.b64encode(profile.avatar.read()).decode('utf-8') if profile.avatar else None,
                    'user_phone': profile.phone if profile else None,
                    'user_address': profile.address if profile else None,
                    'date_joined' : getattr(user, 'date_joined', None),
                    'first_name' : getattr(user, 'first_name', None),
                    'last_name' : getattr(user, 'last_name', None),
                    'gender' : profile.gender if profile else None,
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
    if 'email' in request.POST and 'password' in request.POST and 'username' in request.POST:
        print("Thong bao register qua duoc")
        # Fetch form data
        email = request.POST['email'] 
        password = request.POST['password']
        username = request.POST['username']  
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
            auth.login(request, user,backend='django.contrib.auth.backends.ModelBackend')
            #Profile.objects.create(user=user, gender='', user_address='', user_phone='', user_dob=None, user_avatar=None)
            result['placement'] = 0
            result['message'] = 'Register successfully!'
            print('-------------------------------')
            print(result['message'])
            print('-------------------------------')
            print('Email: ' + email + "\n", 'Password: ' + password + "\n")
    return JsonResponse(result)
def getUserMobile(userid):
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Get User >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    result = {'placement': -1, 'user': None, 'message': ''}
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    result['user'] = {
        'user_id': getattr(user, 'id', None),
        'user_name': user.get_username(),
        'user_email': getattr(user, 'email', None),
        'user_avatar': base64.b64encode(profile.avatar.read()).decode('utf-8') if profile.avatar else None,
        'user_phone': profile.phone if profile else None,
        'user_address': profile.address if profile else None,
        'date_joined' : getattr(user, 'date_joined', None), 
        'first_name' : getattr(user, 'first_name', None),
        'last_name' : getattr(user, 'last_name', None),
        'gender' : profile.gender if profile else None,
    }
    return JsonResponse(result)
@api_view(['POST'])
def updateMobile(request):
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<< Update >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    if (
        request.method == 'POST'
        # and 'email' in request.data
        and 'first_name' in request.data
        and 'last_name' in request.data
        # and 'user_name' in request.data
        and 'user_address' in request.data
        and 'user_phone' in request.data
        and 'user_dob' in request.data
        and 'gender' in request.data
    ):
        print("thong bao da qua duoc")
        user_data = request.data
        # email = user_data['email']
        # user_name = user_data['user_name']
        first_name = user_data['first_name']
        last_name = user_data['last_name']
        gender = user_data['gender']
        user_address = user_data['user_address']
        user_phone = user_data['user_phone']
        user_dob = user_data['user_dob']
        user_id = user_data['user_id']
        user_avatar = request.data.get('user_avatar')  # Assuming 'user_avatar' is a file field
        # from datetime import datetime
        # Decode the image after receiving
        image_string = base64.b64decode(user_avatar)
        user_avatar_config = ContentFile(image_string, name=f"{user_id}_avatar.jpg")
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        # user.username = user_name
        user.first_name = first_name
        user.last_name = last_name
        profile.dob = user_dob
        profile.gender = gender
        profile.address = user_address
        profile.phone = user_phone
        profile.avatar.save(user_avatar_config.name, user_avatar_config)
        profile.save()
        user.save()
        user_response = getUserMobile(user_id)
        user_data_json = user_response.content
        user_data_dict = json.loads(user_data_json)
        result = {'placement': 0, 'message': 'Update Successfully'}
        result['user'] = user_data_dict['user']
        # result['user'] = user_response.data # Update result with user_response.json()
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

@api_view(['POST'])
def authenticate_user(request):
    result = {'placement': -1, 'user': None, 'isLogin': False}
    if request.method == 'POST':
        access_token = request.POST.get('access_token')
        avatarurl = request.POST.get('avatarurl')
        if access_token:
            # Verify access token with Google API
            url = 'https://www.googleapis.com/oauth2/v1/tokeninfo'
            params = {'access_token': access_token}
            response = get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    print("data: ", data)
                    email = data.get('email')
                    google_id = data.get('user_id')
                    avatar = avatarurl
                    user = None
                    username = email.split('@')[0]
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        user = User.objects.create_user(username=username, email=email, password=google_id)
                    profile, created = Profile.objects.get_or_create(user=user)
                    # profile.avatar = avatar
                    
                     # Create or update SocialAccount
                    social_account, _ = SocialAccount.objects.get_or_create(user=user, provider='google')
                    social_account.uid = google_id
                    social_account.extra_data = data
                    social_account.save()
                    if avatar:
                        try:
                            # Download the image from the URL
                            response = requests.get(avatar)
                            if response.status_code == 200:
                                # Save the image to a BytesIO buffer
                                image_content = BytesIO(response.content)
                                # Save the image to the profile's avatar field
                                profile.avatar.save('avatar.jpg', File(image_content))
                                profile.save()
                        except Exception as e:
                            print(f"Error downloading and saving avatar image: {e}")
                            # If there's an error, set the default avatar URL
                            profile.avatar.save('default.jpg', File(open('media/profile_pics/default.jpg', 'rb')))
                            profile.save()
                    else:
                        # Set the default avatar URL
                        profile.avatar.save('default.jpg', File(open('media/profile_pics/default.jpg', 'rb')))
                    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    result['placement'] = 0
                    result['user'] = {
                        'user_id': getattr(user, 'id', None),
                        'user_name': user.get_username(),
                        'user_email': getattr(user, 'email', None),
                        'user_avatar': base64.b64encode(profile.avatar.read()).decode('utf-8') if profile.avatar else None,
                        'user_phone': profile.phone if profile else None,
                        'user_address': profile.address if profile else None,
                        'date_joined' : getattr(user, 'date_joined', None),
                        'first_name' : getattr(user, 'first_name', None),
                        'last_name' : getattr(user, 'last_name', None),
                        'gender' : profile.gender if profile else None,
                    }
                    result['isLogin'] = True
                    return JsonResponse(result)
                else:
                    # Error occurred or token is invalid
                    return JsonResponse({'authenticated': False})
            else:
                # Error handling for Google API request
                return JsonResponse({'error': 'Failed to verify access token'})
        else:
            # Access token not provided in request
            return JsonResponse({'error': 'Access token not provided'})
    else:
        # Invalid request method
        return JsonResponse({'error': 'Invalid request method'})

@api_view(['POST'])
def logoutMobile(request):
    
    result = {'placement': -1, 'message': ''}
    if request.method == 'POST':
        auth.logout(request)
        result['placement'] = 0
        result['message'] = 'Logout Successfully'
        return JsonResponse(result)
    else:
        result['placement'] = 1
        result['message'] = 'Logout Failed'
        return JsonResponse(result)
