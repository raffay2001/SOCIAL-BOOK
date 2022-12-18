from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as Logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import *
from itertools import chain

# Create your views here.

# Controller for the index (home) page
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile_object = Profile.objects.get(user=user_object)
    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    feed_list = list(chain(*feed))
    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile_object, 'posts': feed_list})

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
                login(request, user_login)

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

# Controller for liking a particular post
@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return HttpResponseRedirect(reverse('index'))

# Controller for the user profile page
@login_required(login_url='signin')
def profile(request, pk):
    user_obj = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_obj)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    user_followers = FollowersCount.objects.filter(user=pk).count()
    user_following = FollowersCount.objects.filter(follower=pk).count()


    context = {
        'user_obj': user_obj,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', context=context)

# Controller for following a user
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return HttpResponseRedirect(reverse('profile', args=[user]))
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return HttpResponseRedirect(reverse('profile', args=[user]))
    else:
        return HttpResponseRedirect(reverse('index'))

# Controller for searching a user
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object =  User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile':user_profile, 'username_profile_list': username_profile_list})