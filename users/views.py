import base64
from lib2to3.fixes.fix_input import context
from io import BytesIO
import json
import os
import django
from django.contrib import messages
from django.dispatch import receiver
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
from .models import DetectInfo, Profile
from .forms import ProfileForm
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import pandas as pd
from django.db.models import Count
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from google.auth.transport import requests
from google.auth.transport.requests import Request
from allauth.socialaccount.models import SocialAccount
from django.core.files import File
import requests
from django.contrib.auth.backends import ModelBackend  # Import the appropriate authentication backend class


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
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Custom username validation
        if not username.isalnum():
            return render(request, 'users/register.html', {'error': 'Username must contain only letters and numbers!'})

        # Check if passwords match
        if password1 != password2:
            return render(request, 'users/register.html', {'error': 'Passwords do not match!'})

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'This email is already in use!'})

        try:
            # Check if the username is already in use
            User.objects.get(username=username)
            return render(request, 'users/register.html', {'error': 'Username is already in use!'})
        except User.DoesNotExist:
            # Create the user if username and email are unique
            user = User.objects.create_user(username=username, email=email, password=password1)
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('')  # Redirect to the desired URL after successful registration
    else:
          # Redirect to the desired URL after successful registration
        return render(request, 'users/register.html')

    
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
        profile = Profile.objects.create(user=user, gender='O')
        profile.save()

    form_submitted_successfully = False  # Initialize the variable

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
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

                        profile.avatar.save(filename, avatar_file)

                        # Delete the old avatar file
                        if os.path.exists(old_avatar_path):
                            os.remove(old_avatar_path)
                            print(f"Successfully deleted old avatar file at path: {old_avatar_path}")

            form.save()
            form_submitted_successfully = True  # Set the variable to True upon successful form submission
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profilePage')
        else:
            # Form is invalid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProfileForm(instance=profile, initial={'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

    return render(request, 'users/profilePage.html', {'user': user, 'profile': profile, 'form': form, 'form_submitted_successfully': form_submitted_successfully})

# --------------------Admin-----------------
def logoutAdmin(request):
    auth.logout(request)
    login_url = reverse('customadmin:login') 
    return redirect(login_url)

def get_user_count():
    user_count = Profile.objects.filter(user__is_staff=False).count()
    return user_count

def get_staff_count():
    staff_count = Profile.objects.filter(user__is_staff=True).count()
    return staff_count

def get_detection_count():
    detection_count = DetectInfo.objects.count()
    return detection_count


def gender_disease_chart():
    # Query to get gender and disease information
    data = Profile.objects.filter(user__detectinfo__isnull=False).values('gender').annotate(disease_count=Count('user__detectinfo', distinct=True))

    # Convert data to Pandas DataFrame for easier manipulation
    df = pd.DataFrame(data)

    # Prepare data for Google Chart
    chart_data = [['Gender', 'Amount']]
    for entry in data:
        chart_data.append([entry['gender'], entry['disease_count']])

    context = {'chart_data': chart_data}
    return context    

def result_disease_chart():
    # Get the count of each distinct detect_result value
    result_counts = DetectInfo.objects.values('detect_result').annotate(count=Count('detect_result'))

    # Calculate the total count of detect_info objects
    total_count = DetectInfo.objects.count()

    # Prepare data for Google Chart
    chart_data = [['Detect Result', 'Amount']]
    for entry in result_counts:
        detect_result = entry['detect_result'] if entry['detect_result'] else 'Unknown'
        count = entry['count']
        chart_data.append([detect_result, count])

    context = {'chart_data': chart_data}
    return context

from collections import defaultdict

def login_time_chart():
    # Initialize a dictionary to store login counts for each hour of the day
    login_counts_by_hour = defaultdict(int)

    # Get the last login time for each user
    user_last_login_times = User.objects.exclude(last_login__isnull=True).values_list('last_login', flat=True)

    # Extract the hour component from each login time and increment the corresponding count
    for login_time in user_last_login_times:
        hour = str(login_time.hour)  # Convert hour to string
        login_counts_by_hour[hour] += 1

    # Prepare data for charting
    chart_data = [['Hour of the Day', 'Users Login']]
    for hour in range(24):  # Iterate over 24 hours
        count = login_counts_by_hour[hour]
        chart_data.append([hour, count]) # type: ignore
    return chart_data

from django.contrib.admin.views.decorators import staff_member_required

@login_required
@staff_member_required
def dashboard(request):
    g_disease_chart = gender_disease_chart()
    disease_result_chart = result_disease_chart()
    user_count = get_user_count()
    detection_count = get_detection_count()
    staff_count = get_staff_count()
    time_chart = login_time_chart()

    return render(request, "admin/dashboard.html", {
        'user_count': user_count,
        'detection_count': detection_count,
        'staff_count': staff_count,
        'gender_disease_chart': g_disease_chart,
        'disease_result_chart': disease_result_chart,
        'time_chart' : time_chart,
    })
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
            profile = Profile.objects.get(user=user)
            profile.gender = 'Other'
            profile.save()
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
        'user_dob': profile.dob if profile else None,
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
