from django import forms
from django.db import models
from django.db.models import fields
from django.db.models.query import QuerySet
from django.db.models.query_utils import subclasses
from django.forms import modelformset_factory, formset_factory, BaseModelFormSet
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.http import request
from django.shortcuts import get_object_or_404
from .models import Task, Subject, User, Course, Faculty, Gradebook 
from django.template.defaultfilters import slugify


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',)

class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ('title',)
        labels = {'title': 'Subject'}

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ('faculty', 'year', 'group',)


class TeacherCourseForm(CourseForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TeacherCourseForm, self).__init__(*args, **kwargs)
        teacher = get_object_or_404(User, id=user.id)
        subject_ids = Gradebook.objects.filter(teacher=teacher).values('subject_id')
        self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)

    subject = forms.ModelChoiceField(queryset=None, help_text='Choose one of your subjects')
    fields = ('subject','faculty', 'year', 'group',)

    
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ('title',)
        labels = {'title': 'New assignment'}

class GradeForm(ModelForm):
    class Meta:
        model = Gradebook
        fields = ('grade',)

class StudentForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)