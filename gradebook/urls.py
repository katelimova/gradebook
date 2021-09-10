from django.urls import path, include
from django.contrib import admin
from .views import gradebook, student, teacher, ed_admin


urlpatterns = [ 
    path('', gradebook.HomePageView.as_view(), name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', gradebook.SignUpView.as_view(), name='signup'), #general signup to set user role
    path('accounts/profile/', gradebook.profile, name='profile'),  #url for login_redirect

    path('student/', include(([
        path('signup/', student.signup, name='signup'),
        path('<slug:slug>', student.StudentMainView.as_view(), name='main'),
    ], 'gradebook'), namespace = 'student')),

    path('teacher/', include(([
        path('signup/', teacher.signup, name='signup'),
        path('<slug:slug>', teacher.TeacherMainView.as_view(), name='main'),
        path('course/add/', teacher.course_add, name='course_add'),
        path('subject/add/', teacher.SubjectAddView.as_view(), name='subject_add'),
        path('subject/update/<int:pk>', teacher.subject_update, name='subject_update'),
        path('subject/delete/<int:pk>', teacher.subject_delete, name='subject_delete'),
        path('subject/<int:subject_pk>/course/update/<int:course_pk>', teacher.course_update, name='course_update'),
        path('subject/<int:subject_pk>/course/delete/<int:course_pk>', teacher.course_delete, name='course_delete'),
    ], 'gradebook'), namespace = 'teacher')),
]


