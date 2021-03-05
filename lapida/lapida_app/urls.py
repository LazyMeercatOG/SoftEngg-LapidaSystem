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
  	path('dashboard/',views.dashboard,name='dashboard'),
  	path('menu/',views.menu,name='menu'),
    path('summary/<int:id>',views.summary,name='summary'),
    path('admin/', admin.site.urls),
    url(r'^export-exl/$', views.export, name='export'),
 	  url(r'^export-csv/$', views.export, name='export'),
]
