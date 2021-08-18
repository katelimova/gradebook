from django.contrib.auth import login, authenticate
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.db import models
from django.http import request
from django.views.generic import ListView, CreateView, DetailView
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
            user.save()

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            slug = slugify(f'{first_name, last_name}')

            teacher = Teacher.objects.create(user=user, slug=slug) 
            teacher.save()

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)

        return redirect('homepage')

    else:
        form = RegistrationForm()
    return render(request, 'registration/teacher_signup.html', {'form': form})


class TeacherMainView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'gradebook/teacher_main.html'

    # def get(self, request):
    #     teacher = Teacher.objects.filter(user=self.request.user).get()
    #     subject_list = Gradebook.objects.filter(teacher = teacher).values_list('subject')
    #     subject_list = Gradebook.objects.select_related(user__teacher)

    #     # {{forloop counter }} in templates 
    #     # select_related --- try 

    #     return render(request, self.template_name, ctx)


class AddSubjectsView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher_add_subject.html'
    form_class = AddSubjectForm

    def get_success_url(self):
        teacher = Teacher.objects.get(user=self.request.user)
        return reverse_lazy('teacher:teacher_main', args=[teacher.slug])

    def form_valid(self, form):
        subject = form.save(commit=False)
        subject = Subject.objects.get_or_create(subject=form.cleaned_data['subject'])[0]
        subject.save()

        teacher = Teacher.objects.get(user=self.request.user)
        subject_record = Gradebook.objects.get_or_create(teacher=teacher, subject=subject)[0]
        subject_record.save()
        form.save_m2m()
        return super().form_valid(form)

@login_required
def course_add(request):
    if request.method == "POST":
        form = TeacherAddCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course = Course.objects.get_or_create(
            year=form.cleaned_data['year'],
            group=form.cleaned_data['group'],
            faculty=form.cleaned_data['faculty']
            )[0]
            course.save()

            subject = Subject.objects.get(pk=form.cleaned_data['subject'])
            teacher = Teacher.objects.get(user=request.user)

            if Gradebook.objects.filter(teacher=teacher, subject=subject, course=None).exists():
                course_record = Gradebook.objects.get(teacher=teacher, subject=subject, course=None)
                course_record.course = course
            else:
                course_record = Gradebook.objects.get_or_create(subject=subject, teacher=teacher, course=course)[0]
            
            course_record.save()
            form.save_m2m()
    else:
        form = TeacherAddCourseForm()

    return render(request, 'gradebook/teacher_add_course.html', {'form': form})
