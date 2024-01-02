import base64
import os
import django
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
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
import uuid
from django.core.exceptions import ObjectDoesNotExist

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
        profile = Profile(user=user)
        profile.save()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Get the avatar file from the form
            avatar_file = form.cleaned_data['avatar']

            # Check if a new avatar file was provided
            if avatar_file:
                # Check if the profile has an existing avatar
                if profile.avatar and profile.avatar.name:
                    # Delete the old avatar file
                    profile.avatar.delete(save=False)

                # Save the new avatar file, rename it based on user ID
                # user_id = profile.user.id
                # filename = f"profile_{user_id}_{avatar_file.name}"
                # profile.avatar.save(filename, avatar_file)

            # Save the form, which also saves the profile
            form.save()

            return redirect('profile')

    else:
        # Pass the user data to the form when instantiating it
        form = ProfileForm(instance=profile, initial={'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

    return render(request, 'users/view_profile.html', {'user': user, 'profile': profile, 'form': form})


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
        # jpg_as_np = np.frombuffer(image_string, dtype=np.uint8)
        # original_image = cv2.imdecode(jpg_as_np, flags=1)
        user_avatar_config = ContentFile(image_string, name=f"{user_id}_avatar.jpg")

        # Resize the image to a specific width and height
        # new_width, new_height = 300, 300
        # original_image_resize = cv2.resize(original_image, (new_width, new_height))
        # Convert NumPy array to a file-like object
        # image_io = io.BytesIO()
        # Image.fromarray(original_image_resize).save(image_io, format='JPEG')
        # image_io.seek(0)
        user = User.objects.get(id=user_id)
        # filename = f"{user_id}_{str(uuid.uuid4())[:8]}_{original_image_resize}"

        profile = Profile.objects.get(user=user)
        user.username = user_name
        user.email = email
        profile.address = user_address
        profile.phone = user_phone
        profile.dob = user_dob
        profile.avatar.save(user_avatar_config.name, user_avatar_config)

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



