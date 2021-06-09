from django.contrib import admin
from django.urls import path
from .views import test_mainpage

app_name = 'monitor'
urlpatterns = [
    path('', test_mainpage, name='index')
]