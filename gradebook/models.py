from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.defaultfilters import first, slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, email, password, course=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if user.role == User.STUDENT or user.role == User.STUD_REP:
            user.course = course
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
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f' {self.first_name} {self.last_name}'


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
        return f'{self.year} year, {self.group} group, faculty of {self.faculty}'

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

    def courses_of_subject(self):
        subject_id = Subject.objects.filter(subject=self.subject)
        course_ids = Gradebook.objects.filter(subject_id__in=subject_id).values('course_id')
        return Course.objects.filter(id__in=course_ids).order_by('year')

class Assignment(models.Model):
    assignment = models.CharField(max_length=100)
    def __str__(self):
        return self.assignment


class Gradebook(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='students')
    teacher =  models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='teachers')
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True)
    grade = models.PositiveIntegerField(
        null=True, blank=True,
        validators = [MinValueValidator(1, "The grade can't be less than 1"),
        MaxValueValidator(100, "The grade can't be greater than 100")]
    )

    def __str__(self):
        return f'{self.student} has got {self.grade} in {self.subject} for {self.assignment}'

