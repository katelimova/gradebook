from django.template.defaultfilters import slugify
from django.views.generic.edit import CreateView
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from gradebook.forms import RegistrationForm, CourseForm
from django.contrib import messages
from gradebook.models import Course, Faculty, Student, User
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        form_course = CourseForm(request.POST)

        if form.is_valid() and form_course.is_valid():
            course = form_course.save(commit=False)

            year = form_course.cleaned_data['year']
            group = form_course.cleaned_data['group']
            faculty = form_course.cleaned_data['faculty']

            if Course.objects.filter(year=year, group=group, faculty=faculty).exists():
                course = Course.objects.get(year=year, group=group, faculty=faculty)
            else:
                course = Course.objects.create(year=year, group=group, faculty=faculty)
            course.save()

            user = form.save(commit=False)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user.slug = slugify(f'{first_name, last_name}') 
            user.save()

            student = Student.objects.create(user=user, course=course)
            student.save()
            form.save_m2m()
            form_course.save_m2m()

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)

            return redirect(reverse('student:main', args=[request.user.slug]))
    else:
        form = RegistrationForm()
        form_course = CourseForm()

    return render(request, 'registration/student_signup.html', {'form': form, 'form_course': form_course})


class StudentMainView(LoginRequiredMixin, TemplateView):
    template_name = 'gradebook/student/main.html'

