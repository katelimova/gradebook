from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
# from gradebook.forms import StudentSignUpForm
from django.contrib import messages
from gradebook.models import User


# def test(request):
#     if request.user.role == User.STUDENT:
#         return HttpResponse('ASDFDFDjfjfjfj')
#     return HttpResponse('a')

class HomePageView(TemplateView):
    template_name = 'gradebook/homepage.html'

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'





