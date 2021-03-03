from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, ProfileForm, User_PlaceForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .decorators import unathenticated_user, allowed_users
from django.contrib.auth.models import Group
from .models import User_Place, MasterData_Revised
from .resources import MasterData_RevisedResource
from django.core.exceptions import ObjectDoesNotExist



@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin'])
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
				group = Group.objects.get(name="customer")	
				user.groups.add(group)		
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

def create_dead(request):
	if request.method == "POST":
		form = User_PlaceForm(request.POST)
		uid = request.POST.get('uid')
		try:
			dead = MasterData_Revised.objects.get(uid=uid)
		except ObjectDoesNotExist:
			messages.error(request, 'The UID you inputted was not found in our database')
		if form.is_valid():
			dead = form.save(commit=False)
			dead.user = request.user
			dead.uid = MasterData_Revised.objects.get(uid=uid)
			dead.save()
			return redirect('profile')
	else:
		form = User_PlaceForm()
	context = {'form':form}
	return render(request, 'lapida_app/register_dead.html',context)

def profile(request):
	query_results = User_Place.objects.filter(user=request.user)
	dead_profile = []
	for dead in query_results:
		dead_profile.append(MasterData_Revised.objects.get(uid=dead))
	context = {'form':dead_profile}
	return render(request, 'lapida_app/profile.html',context)

def export(request):
    member_resource = MasterData_RevisedResource()
    dataset = member_resource.export()
    #response = HttpResponse(dataset.csv, content_type='text/csv')
    #response['Content-Disposition'] = 'attachment; filename="member.csv"'
    #response = HttpResponse(dataset.json, content_type='application/json')
    #response['Content-Disposition'] = 'attachment; filename="persons.json"'
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="persons.xls"'
    return response




# Create your views here.
