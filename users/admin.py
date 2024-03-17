from django.contrib import admin
from django.shortcuts import render, redirect
from .models import Profile, DetectInfo
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib.admin import AdminSite



# Register your models here.
admin.site.register(Profile)
admin.site.register(DetectInfo)

class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse('dashboard')

class CustomAdminSite(AdminSite):
    def login(self, request, extra_context=None):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))
        else:
            return CustomLoginView.as_view(template_name='admin/login.html')(request)

admin_site = CustomAdminSite(name='customadmin')
