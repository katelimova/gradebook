from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.http import request
from .models import User, Student, Teacher, Course, Faculty, Gradebook 


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class AddCourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['faculty', 'year', 'group']

