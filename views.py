"""from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib import messages
from .models import UserData
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
def login_page(request):
    return render(request, 'appln/login.html')

def index_view(request):
    return render(request, 'appln/index.html')



def signup_view(request):
    if request.method == 'POST': #to get html
        email = request.POST.get('email')
        password = request.POST.get('password')
        coupon = request.POST.get('coupon')

        # Hash the password before saving
        hashed_password = make_password(password)

        # Save user data to the database
        user = UserData(email=email, password=hashed_password, coupon=coupon)
        user.save()

        return render(request, 'appln/signup.html', {'success': 'Signup Successful!'})

    return render(request, 'appln/signup.html')

def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserData.objects.get(email=email)

            # Check hashed password
            if check_password(password, user.password):
                # Login success
                return redirect('index')
            else:
                # Password mismatch
                return render(request, 'appln/login.html', {'error': 'Invalid password!'})

        except UserData.DoesNotExist:
            return redirect('signup')  # Redirect to signup if user not found

    return render(request, 'appln/login.html')"""

# views.py
"""from django.shortcuts import render

def index(request):
    return render(request, 'index.html')  # Assuming React build index.html is here"""

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


def auth_login(request, provider):
    base_url = f"https://{settings.AUTH0_DOMAIN}/authorize"
    params = {
        "client_id": settings.AUTH0_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.AUTH0_CALLBACK_URL,
        "scope": "openid profile email",
        "connection": provider  # 'google-oauth2', 'facebook', 'apple'
    }
    return redirect(f"{base_url}?{urllib.parse.urlencode(params)}")


def auth_callback(request):
    # Get the code from the request's query parameters
    code = request.GET.get('code')
    
    # Ensure we have a code (it should be provided after successful authentication)
    if not code:
        return HttpResponse("Missing 'code' parameter in callback.")

    # Define the token URL for exchanging the authorization code for an access token
    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    
    # Prepare the token request payload
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.AUTH0_CALLBACK_URL
    }

    # Make the POST request to exchange the code for an access token
    token_res = requests.post(token_url, json=data).json()

    # Check if the response contains an id_token
    id_token = token_res.get('id_token')

    if not id_token:
        return HttpResponse("Authentication failed.")

    # Request user information using the access token
    userinfo_url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
    headers = {'Authorization': f"Bearer {token_res['access_token']}"}
    userinfo = requests.get(userinfo_url, headers=headers).json()

    # Store user data in the database
    email = userinfo['email']
    provider = userinfo['sub'].split('|')[0]  # Extract provider (google-oauth2, facebook, apple)

    # Check if the user exists, if not create the user in the database
    if not UserData.objects.filter(email=email).exists():
        UserData.objects.create(
            email=email,
            password=make_password(''),  # Empty password as it's social login
            provider=provider
        )

    return HttpResponse(f"Logged in as {email} using {provider}")








