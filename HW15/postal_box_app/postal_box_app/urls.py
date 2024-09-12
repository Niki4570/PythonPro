from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('register/', views.register),
    path('login/', views.login),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('parcel/', include('parcel.urls')),
    path('post_machine/', include('post_machine.urls')),
]
