from gradebook.forms import AddCourseForm
from django.urls import path, include, reverse_lazy
from django.contrib import admin
from .views import gradebook, student, teacher, ed_admin




urlpatterns = [ 
    path('', gradebook.HomePageView.as_view(), name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', gradebook.SignUpView.as_view(), name='signup'), #general signup to choose role

    path('student/', include(([
        path('signup/', student.signup, name='student_signup'),
        path('<slug:slug>', student.StudentMainView.as_view(), name='student_main'),
    ], 'gradebook'), namespace = 'student')),

    path('teacher/', include(([
        path('signup/', teacher.signup, name='teacher_signup'),
        path('<slug:slug>', teacher.TeacherMainView.as_view(), name='teacher_main'),
        path('course/add/', teacher.AddCoursesView.as_view(), name='teacher_add_course'),
    ], 'gradebook'), namespace = 'teacher')),

]


