from django import forms
from django.db.models import fields
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.http import request
from .models import Subject, User, Student, Teacher, Course, Faculty, Gradebook 


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class AddSubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ['subject']

class AddCourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['faculty', 'year', 'group']


class TeacherAddCourseForm(AddCourseForm):
    SUBJECTS = Subject.objects.all().values_list()
    subject = forms.ChoiceField(choices=SUBJECTS)
    fields = ['subject','faculty', 'year', 'group']
