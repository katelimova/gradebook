from django import forms
from django.db import models
from django.db.models import fields
from django.db.models.query import QuerySet
from django.db.models.query_utils import subclasses
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.http import request
from .models import Subject, User, Student, Teacher, Course, Faculty, Gradebook 


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ['subject']

class StudentCourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['faculty', 'year', 'group']


class TeacherCourseForm(StudentCourseForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TeacherCourseForm, self).__init__(*args, **kwargs)
        teacher = Teacher.objects.filter(user=user)
        subject_ids = Gradebook.objects.filter(teacher__in=teacher).values('subject_id')
        self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)

    subject = forms.ModelChoiceField(queryset=None, help_text='Choose one of your subjects')
    fields = ['subject','faculty', 'year', 'group']
    
