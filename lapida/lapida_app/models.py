from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O','Others'),
    )

class Profile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES) 
	phone = PhoneNumberField()
	def __str__(self):
		return f'{self.user.username} Profile'
