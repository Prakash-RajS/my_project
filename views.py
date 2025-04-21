import urllib.parse
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .models import UserData
from django.contrib.auth.hashers import make_password


def index(request):
    return render(request, 'index.html')


def signup_view(request):
    return render(request, 'appln/signup.html')


def login_view(request):
    return render(request, 'appln/login.html')
