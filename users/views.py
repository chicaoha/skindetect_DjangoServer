from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
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
        return render(request, 'users/phat_log.html')
    

def logout(request):
    auth.logout(request)
    return redirect('index')

# @login_required
# def profile(request):
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
        # args = {}
        # args.update(csrf(request))
        # args['form'] = form
        # args['profile_form'] = profile_form
    # return render(request, 'users/profile.html')