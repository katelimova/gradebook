from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy, reverse
from django.views.generic.base import TemplateView
from django.contrib import messages
from gradebook.models import User

class HomePageView(TemplateView):
    template_name = 'gradebook/homepage.html'

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

@login_required
def profile(request):
    if request.user.role == User.STUDENT:
        return HttpResponseRedirect(reverse('student:main', args=[request.user.slug]))
    elif request.user.role == User.TEACHER:
        return HttpResponseRedirect(reverse('teacher:main', args=[request.user.slug]))
    else:
        return HttpResponseRedirect('homepage')








