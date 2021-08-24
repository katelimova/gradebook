from django.contrib.auth import login, authenticate
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.db import models
from django.http import request
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.views.generic.edit import FormView
from gradebook.forms import RegistrationForm, AddCourseForm, AddSubjectForm, TeacherAddCourseForm
from gradebook.models import Course, Subject, User, Teacher, Gradebook
from django.shortcuts import get_object_or_404, render, redirect
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

            teacher = Teacher.objects.create(user=user)
            teacher.save()

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)

        return redirect(reverse('teacher:teacher_main', args=[request.user.slug]))

    else:
        form = RegistrationForm()
    return render(request, 'registration/teacher_signup.html', {'form': form})

class TeacherMainView(LoginRequiredMixin, ListView):
    template_name = 'gradebook/teacher_main.html'
    def get_queryset(self):
        teacher = Teacher.objects.filter(user=self.request.user)
        subject_ids = Gradebook.objects.filter(teacher__in=teacher).values('subject_id')
        queryset = Subject.objects.filter(id__in=subject_ids)
        return queryset

class AddSubjectsView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher_add_subject.html'
    form_class = AddSubjectForm

    def get_success_url(self):
        return reverse('teacher:teacher_main', args=[self.request.user.slug])

    def form_valid(self, form):
        subject = form.save(commit=False)
        subject = Subject.objects.get_or_create(subject=form.cleaned_data['subject'])[0]
        subject.save()

        teacher = Teacher.objects.get(user=self.request.user)

        if not Gradebook.objects.filter(teacher=teacher, subject=subject).exists():
            subject_record = Gradebook.objects.create(teacher=teacher, subject=subject)
            subject_record.save()
        form.save_m2m()
        return super().form_valid(form)


@login_required
def course_add(request):
    if request.method == "POST":
        form = TeacherAddCourseForm(request.user, request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course = Course.objects.get_or_create(
            year=form.cleaned_data['year'],
            group=form.cleaned_data['group'],
            faculty=form.cleaned_data['faculty']
            )[0]
            course.save()
            subject = Subject.objects.get(subject=form.cleaned_data['subject'])
            teacher = Teacher.objects.get(user=request.user)

            try:
                course_record = Gradebook.objects.get(teacher=teacher, subject=subject, course=None)
                course_record.course = course  
            except:
                course_record = Gradebook.objects.get_or_create(subject=subject, teacher=teacher, course=course)[0]
            
            course_record.save()
            form.save_m2m()     

        return redirect(reverse_lazy('teacher:teacher_main', args=[request.user.slug]))

    else:
        form = TeacherAddCourseForm(request.user)
    return render(request, 'gradebook/teacher_add_course.html', {'form': form})

