from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, ProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .decorators import unathenticated_user


@login_required(login_url='login')
def index(request):
	return render(request, 'lapida_app/index.html')

@unathenticated_user
def loginPage(request):
	message_error = ''
	message_error_1 = ''
	if request.user.is_authenticated:
		return redirect('home-view')
	else:
		if request.method == "POST":
			username=request.POST.get('username')
			password=request.POST.get('password')
			user = authenticate(request,username=username,password=password)
			if user is not None:
				login(request,user)
				return redirect('home-view')
			else:
				message_error = messages.info(request,'Username or Password is incorrect')
				message_error_1 = "Username or Password is incorrect"
		context ={'message_error' :message_error_1}
		return render(request, 'lapida_app/login.html', context)



def logoutUser(request):
	logout(request)
	return redirect('login')

@unathenticated_user
def register(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	else:
		if request.method == "POST":
			form = CreateUserForm(request.POST)
			form_1 = ProfileForm(request.POST)
			gender = request.POST.get('gender')
			form_1.gender = gender
			if form.is_valid() and form_1.is_valid():
				user = form.save()
				form_1 = form_1.save(commit=False)			
				form_1.user = user
				form_1.save()
				username = form.cleaned_data.get('username')
				messages.success(request, 'Account is created for ' + username)
				request.session['success'] = "Account is created for " + username
				return redirect('login')
		else:
			form = CreateUserForm()
			form_1 = ProfileForm()
			for msg in form.error_messages:
			   messages.error(request, f"{msg}: {form.error_messages[msg]}")
			   print(msg)
		context = {'form':form,'form_1':form_1}
		return render(request, 'lapida_app/register.html',context)

# Create your views here.
