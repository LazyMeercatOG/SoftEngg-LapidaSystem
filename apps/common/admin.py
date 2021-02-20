from django.contrib import admin
from .models import User, Caretaker

# Register your models here.
admin.site.register(User)
admin.site.register(Caretaker)