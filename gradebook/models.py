from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    STUDENT = 1
    STUD_REP = 2
    TEACHER = 3
    ED_ADMIN = 4
    ROLES = (
        (STUDENT, 'student'),
        (STUD_REP, 'student representative'),
        (TEACHER, 'teacher'),
        (ED_ADMIN, 'education administrator'),
    )
    role = models.PositiveIntegerField(choices=ROLES, default=STUDENT)

    def __str__(self):
        return f' {self.email}, {self.get_role_display()}'


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    subjects = models.ManyToManyField('Subject', through='Gradebook')
    teachers = models.ManyToManyField('Teacher', through='Gradebook')
    slug = models.SlugField(unique=True)
    # class Meta:
    #     ordering = ['lastname']
    #     unique_together = [['firstname', 'lastname', 'course']]

    def __str__(self):
        return f' {self.user.first_name}, {self.user.last_name}'


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, default='')
    subjects = models.ManyToManyField('Subject', through='Gradebook')
    students = models.ManyToManyField('Student', through='Gradebook')
    courses = models.ManyToManyField('Course', through='Gradebook')

    def __str__(self):
        return f' {self.user.first_name}, {self.user.last_name}'

class Course(models.Model):

    YEAR_OF_STUDY = (
        (1, 'first year'),
        (2, 'second year'),
        (3, 'third year'),
        (4, 'fourth year'),
    )
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    year = models.PositiveIntegerField(choices=YEAR_OF_STUDY, default=1)
    group = models.PositiveIntegerField()
    def __str__(self):
        return f'{self.year} year, {self.faculty}, {self.group} group'

class Faculty(models.Model):
    faculty = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'Faculties'
    def __str__(self):
        return self.faculty

class Subject(models.Model):
    subject = models.CharField(max_length=100)
    def __str__(self):
        return self.subject

class Assignment(models.Model):
    assignment = models.CharField(max_length=100)
    def __str__(self):
        return self.assignment


class Gradebook(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)
    teacher =  models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True, blank=True)
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True)
    grade = models.PositiveIntegerField(
        null=True, blank=True,
        validators = [MinValueValidator(1, "The grade can't be less than 1"),
        MaxValueValidator(100, "The grade can't be greater than 100")]
    )

    def __str__(self):
        return f'{self.student} has got {self.grade} in {self.subject} for {self.assignment}'
