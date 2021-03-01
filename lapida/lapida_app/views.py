from django.shortcuts import render


#@login_required(login_url='login')
def index(request):
	return render(request, 'lapida_app/index.html')


# Create your views here.
