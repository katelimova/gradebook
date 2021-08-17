from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import Student, Teacher, Course, Faculty, Subject, Gradebook, Assignment
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# class StudentAdmin(ModelAdmin):
#     first_name = User.objects.filter('first_name').values('first_name')
#     fields = ['first_name']

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(Gradebook)
admin.site.register(Assignment)
admin.site.register(User, CustomUserAdmin)





