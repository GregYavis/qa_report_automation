from django.contrib import admin
from django.urls import path
from .views import MainPage

app_name = 'monitor'
urlpatterns = [
    path('', MainPage.as_view(), name='main-page'),
]