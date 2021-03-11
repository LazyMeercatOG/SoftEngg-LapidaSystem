from django.forms import ModelForm
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import (
    PhoneNumberPrefixWidget,
    PhoneNumberInternationalFallbackWidget,
    PhonePrefixSelect,
)
from .models import Profile, User_Place, MasterData_Revised, Order_User
from bootstrap_datepicker_plus import DatePickerInput
import datetime


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "input--style-4"}),
            "first_name": forms.TextInput(attrs={"class": "input--style-4"}),
            "last_name": forms.TextInput(attrs={"class": "input--style-4"}),
            "password1": forms.PasswordInput(),
            "password2": forms.PasswordInput(),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        phone = PhoneNumberField()
        fields = ["middle_name", "phone"]
        widgets = {
            "middle_name": forms.TextInput(attrs={"class": "input--style-4"}),
            "phone": PhoneNumberPrefixWidget(),
        }


class User_PlaceForm(forms.ModelForm):
    class Meta:
        model = User_Place
        uid = models.CharField(max_length=50)
        fields = ["uid"]
        widgets = {
            "uid": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
        }
        # def clean_uid(self):
        # 	uid = self.cleaned_data.get('uid')
        # 	try:
        # 	   dead = MasterData_Revised.objects.get(uid = uid)
        # 	   print(dead)
        # 	except ObjectDoesNotExist:
        # 	   raise forms.ValidationError('The UID you inputted was not found in our database')
        # 	return uid


class EventForm(forms.Form):
    birth_date = forms.DateField(
        widget=DatePickerInput(attrs={"required": True})
    )


# widgets = {"birth_date": DatePickerInput(attrs={"required": True})}


class Order_UserForm(forms.ModelForm):
    class Meta:
        model = Order_User
        fields = ["order_date"]
        widgets = {
            "order_date": DatePickerInput(
                attrs={"required": True},
                options={
                    "minDate": (datetime.datetime.today().strftime("%m-%d-%Y"))
                },
            )
        }
