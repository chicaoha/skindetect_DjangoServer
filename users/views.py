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