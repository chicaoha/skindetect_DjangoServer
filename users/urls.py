import tarfile
from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
from . import views
from . import viewDetect
# from django.conf.urls import patterns, url
from .admin import admin_site


urlpatterns = [
    # ----------admin---------------
    path('admin', admin_site.urls),  # Use admin_site.urls instead of admin.site.urls
    path('dashboard', views.dashboard, name='dashboard'),
    path('logoutAdmin', views.logoutAdmin, name='logoutadmin'),

    #-----------web----------------
    path('', views.index, name=''),
    path('home', views.index, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('about', views.about, name='about'),
    path('FAQ', views.FAQ, name='FAQ'),
    path('contact', views.contact, name='contact'),
    path('blog1', views.blog1, name='blog1'),
    path('blog2', views.blog2, name='blog2'),
    path('blog3', views.blog3, name='blog3'),
    path('profilePage', views.profile, name='profilePage'),
    path('page404', views.page404, name='page404'),
    path('detect', viewDetect.detectImage, name='detect'),
    path('showResult', viewDetect.showResult, name='showResult'),
    path('detectHistory', viewDetect.history, name='detectHistory'),
    path('delete', viewDetect.deleteDetectResult, name='delete'),
    path('mobileApp', views.mobileApp, name='mobileApp'),
    path('forgotPassword', views.forgotPassword, name='forgotPassword'),
    path('aboutDisease', viewDetect.aboutDisease, name='aboutDisease'),

    #-----------profile mobile api----------------
    path('loginMobile', views.loginMobile, name='loginMobile'),
    path('registerMobile', views.registerMobile, name='registerMobile'),
    path('updateMobile', views.updateMobile, name='updateMobile'),
    #-----------detect mobile api----------------
    path('getimage' ,viewDetect.getimage, name='getimage'),
    path('getHistory', viewDetect.getHistory, name='getHistory'),
    path('deleteImage', viewDetect.deleteImage, name='deleteImage'),
    path('getDetail', viewDetect.getDetail, name='getDetail'),
    path('getListDetail', viewDetect.getListDetail, name='getListDetail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

