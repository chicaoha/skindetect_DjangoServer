from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
from . import views

# from django.conf.urls import patterns, url


urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('loginMobile', views.loginMobile, name='loginMobile'),
    path('registerMobile', views.registerMobile, name='registerMobile'),
    path('updateMobile', views.updateMobile, name='updateMobile'),
    path('getimage' ,views.getimage, name='getimage'),
]



# urlpatterns = patterns('users.views',
#                        url(r'^view_profile/$', 'view_profile', name ='view_profile'),
#                        url(r'^view_profile/edit_profile/$', 'edit_profile', name ='edit_profile'))

# urlpatterns = [
#                   url(r'^accounts/', include('accounts.urls', namespace='accounts')),
#               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)