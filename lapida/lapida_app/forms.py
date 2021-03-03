from django.forms import ModelForm
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from .models import Profile, User_Place


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['first_name','last_name','username','email','password1','password2']
		widgets = {
            'username': forms.TextInput(attrs={'class':'input--style-4'}),
            'first_name': forms.TextInput(attrs={'class':'input--style-4'}),
            'last_name': forms.TextInput(attrs={'class':'input--style-4'}),
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),            
            }


class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		gender = models.CharField(max_length=1) 
		phone = PhoneNumberField()
		fields = ['gender', 'phone']
		widgets = {
            'phone': forms.TextInput(attrs={'class':'input--style-4'}), 
            'gender': forms.TextInput(), 
            }
	
class User_PlaceForm(forms.ModelForm):
	class Meta:
		model = User_Place
		uid = models.CharField(max_length=50)
		fields = ['uid']
		widgets = {
			'uid': forms.TextInput(attrs={'class':'form-control', 'required': True}),			
            }




