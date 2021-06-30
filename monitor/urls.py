from django.contrib import admin
from django.urls import path
from .views import MainPage
from django.views.decorators.csrf import csrf_exempt
app_name = 'monitor'
urlpatterns = [
    path('', csrf_exempt(MainPage.as_view()), name='main-page'),
]