from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='home-view'),
    #path('register/', views.register, name='register'),
    #path('login/',views.loginPage, name='login'),
  	#path('logout/',views.logoutUser,name='logout'),
]
