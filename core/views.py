from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as Logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import *

# Create your views here.

# Controller for the index (home) page
@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')

# Controller for the signup page
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Checking if the two passwords are equal or not.
        if password == password2:
            # Checking if the user with same email exists in the dB or not
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Taken')
                return HttpResponseRedirect(reverse('signup'))
            # Checking if the user with same username exists in the dB or not
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return HttpResponseRedirect(reverse('signup'))
            # If not create the new user
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return HttpResponseRedirect(reverse('signup'))
        else:
            messages.info(request, 'Password Not Matching.')
            return HttpResponseRedirect(reverse('signup'))
    return render(request, 'signup.html')

# Controller for the signin page
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        # Checking the validity of the user
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.info(request, 'Credentials Invalid')
            return HttpResponseRedirect(reverse('signin'))

    return render(request, 'signin.html')

# Controller for logging the user out
@login_required(login_url='signin')
def logout(request):
    Logout(request)
    return HttpResponseRedirect(reverse('signin'))