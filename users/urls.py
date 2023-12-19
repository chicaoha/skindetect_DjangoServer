from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
# from django.conf.urls import patterns, url
# from django.conf.urls import include, url

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = patterns('users.views',
#                        url(r'^view_profile/$', 'view_profile', name ='view_profile'),
#                        url(r'^view_profile/edit_profile/$', 'edit_profile', name ='edit_profile'))

# urlpatterns = [
#                   url(r'^accounts/', include('accounts.urls', namespace='accounts')),
#               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)