from django.contrib.auth import login, authenticate
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.template import defaultfilters
from django.urls import reverse_lazy, reverse
from django.db import models
from django.http import request
from django.views.generic import View, ListView, DetailView, TemplateView, UpdateView
from django.views.generic.edit import DeleteView, FormView
from gradebook.forms import RegistrationForm, SubjectForm, TeacherCourseForm, CourseForm
from gradebook.models import Course, Subject, User, Teacher, Gradebook
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.template.defaultfilters import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == 'POST': 
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.TEACHER
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user.slug = slugify(f'{first_name, last_name}')
            user.save()
            Teacher.objects.create(user=user)

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)
        return redirect(reverse('teacher:main', args=[request.user.slug]))

    else:
        form = RegistrationForm()
    return render(request, 'registration/teacher_signup.html', {'form': form})

class TeacherMainView(LoginRequiredMixin, ListView):
    template_name = 'gradebook/teacher/main.html'
    def get_queryset(self):
        teacher = Teacher.objects.filter(user=self.request.user)
        subject_ids = Gradebook.objects.filter(teacher__in=teacher).values('subject_id')
        queryset = Subject.objects.filter(id__in=subject_ids).order_by('subject')
        return queryset

class SubjectAddView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher/subject_form.html'
    form_class = SubjectForm
    def get_success_url(self):
        return reverse('teacher:main', args=[self.request.user.slug])
    def form_valid(self, form):
        subject = Subject.objects.get_or_create(subject=form.cleaned_data['subject'])[0]
        teacher = Teacher.objects.get(user=self.request.user)
        if not Gradebook.objects.filter(teacher=teacher, subject=subject).exists():
            Gradebook.objects.create(teacher=teacher, subject=subject)
        return super().form_valid(form)

@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            new_subject = Subject.objects.get_or_create(subject=form.cleaned_data['subject'])[0]
            teacher = Teacher.objects.get(user=request.user)
            subject_record = Gradebook.objects.filter(subject=subject, teacher=teacher)
            subject_record.update(subject=new_subject)
        return redirect(reverse('teacher:main', args=[request.user.slug]))
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'gradebook/teacher/subject_form.html', {'form': form})


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    teacher = Teacher.objects.get(user=request.user)
    if request.method == 'POST':
        subject_records = Gradebook.objects.filter(subject=subject, teacher=teacher)
        subject_records.delete()
        return redirect(reverse('teacher:main', args=[request.user.slug]))
    return render(request, 'gradebook/teacher/subject_confirm_delete.html', {'subject': subject})


@login_required
def course_add(request):
    if request.method == "POST":
        form = TeacherCourseForm(request.user, request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course = Course.objects.get_or_create(
            year=form.cleaned_data['year'],
            group=form.cleaned_data['group'],
            faculty=form.cleaned_data['faculty']
            )[0]
            subject = Subject.objects.get(subject=form.cleaned_data['subject'])
            teacher = Teacher.objects.get(user=request.user)
    
            try:
                course_record = Gradebook.objects.get(teacher=teacher, subject=subject, course=None)
                course_record.course = course  
            except:
                course_record = Gradebook.objects.get_or_create(subject=subject, teacher=teacher, course=course)[0]           
            course_record.save()
            form.save_m2m()     
        return redirect(reverse_lazy('teacher:main', args=[request.user.slug]))
    else:
        form = TeacherCourseForm(request.user)
    return render(request, 'gradebook/teacher/course_form.html', {'form': form})

@login_required
def course_update(request, subject_pk, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            new_course = Course.objects.get_or_create(
                faculty=form.cleaned_data['faculty'],
                year = form.cleaned_data['year'],
                group = form.cleaned_data['group'],
                )[0]
            teacher = Teacher.objects.get(user=request.user)
            
            course_record = Gradebook.objects.filter(course=course, subject=subject, teacher=teacher)
            course_record.update(course=new_course)
        return redirect(reverse('teacher:main', args=[request.user.slug]))
    else:
        form = CourseForm(instance=course)
    return render(request, 'gradebook/teacher/course_update.html', {'form': form, 'subject': subject})

@login_required
def course_delete(request, subject_pk, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    teacher = Teacher.objects.get(user=request.user)
    
    if request.method == 'POST':
        Gradebook.objects.filter(course=course, subject=subject, teacher=teacher).delete()
        return redirect(reverse('teacher:main', args=[request.user.slug]))
    return render(request, 'gradebook/teacher/course_confirm_delete.html', {'course': course, 'subject': subject})


    