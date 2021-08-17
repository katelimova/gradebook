from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy, reverse
from django.db import models
from django.http import request
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.views.generic.edit import FormView
from gradebook.forms import RegistrationForm, AddCourseForm
from gradebook.models import Course, User, Teacher, Gradebook
from django.shortcuts import render, redirect
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

class AddCoursesView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher_add_course.html'
    form_class = AddCourseForm

    def get_success_url(self):
        teacher = Teacher.objects.filter(user=self.request.user).get()
        return reverse_lazy('teacher:teacher_main', args=[teacher.slug])

    def form_valid(self, form):
        course = form.save(commit=False)
        year = form.cleaned_data['year']
        group = form.cleaned_data['group']
        faculty = form.cleaned_data['faculty']

        if Course.objects.filter(year=year, group=group, faculty=faculty).exists():
            course = Course.objects.get(year=year, group=group, faculty=faculty)
        else:
            course = Course.objects.create(year=year, group=group, faculty=faculty)
        course.save()

        teacher = Teacher.objects.filter(user=self.request.user).get()

        gb = Gradebook.objects.create(teacher=teacher, course=course)
        gb.save()
        form.save_m2m()
        return super().form_valid(form)



# @login_required
# def addcourses(request):
#     form = 
#     return render(request, '', ctx)