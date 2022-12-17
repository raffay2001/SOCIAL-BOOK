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
    path('settings', views.settings, name='settings')
]