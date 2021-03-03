from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='home-view'),
    path('register/', views.register, name='register'),
    path('login/',views.loginPage, name='login'),
  	path('logout/',views.logoutUser,name='logout'),
  	path('register_dead/',views.create_dead,name='create-dead'),
    path('profile/',views.profile,name='profile'),
    path('admin/', admin.site.urls),
    url(r'^export-exl/$', views.export, name='export'),
 	url(r'^export-csv/$', views.export, name='export'),
]
