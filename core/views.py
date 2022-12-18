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
    user_object = User.objects.get(username=request.user.username)
    user_profile_object = Profile.objects.get(user=user_object)
    return render(request, 'index.html', {'user_profile': user_profile_object})

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
                user_login = authenticate(username=username, password=password)
                login(user_login)

                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return HttpResponseRedirect(reverse('settings'))
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

# Controller for the settings page
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return HttpResponseRedirect(reverse('settings'))

    return render(request, 'setting.html', context={'user_profile':user_profile})


# Controller for uploading a post
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('index'))