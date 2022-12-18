from django.urls import path
from . import views

urlpatterns = [
    # home page route
    path('', views.index, name='index'),
    # authentication routes
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    # account settings route
    path('settings', views.settings, name='settings'),
    # post uploading route
    path('upload', views.upload, name='upload'),
    # route for liking a post
    path('like-post', views.like_post, name='like-post'),
    # route for the profile page
    path('profile/<str:pk>/', views.profile, name='profile'),
    # route for following a user
    path('follow', views.follow, name='follow'),
    # route for searching a user
    path('search', views.search, name='search')
]