from django.contrib.auth import login, authenticate
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, TemplateView, UpdateView, CreateView
from django.views.generic.edit import DeleteView, FormView
from gradebook.forms import TaskForm, GradeForm, RegistrationForm, StudentForm, SubjectForm, TeacherCourseForm, CourseForm
from gradebook.models import Task, Course, Subject, User, Gradebook
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.template.defaultfilters import first, last, slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



def signup(request):
    if request.method == 'POST': 
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.TEACHER
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user.slug = slugify(f'{first_name, last_name}')
            user.save()

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)
        return redirect(reverse('teacher_main', args=[request.user.slug]))

    else:
        form = RegistrationForm()
    return render(request, 'registration/teacher_signup.html', {'form': form})

class TeacherMainView(LoginRequiredMixin, ListView):
    template_name = 'gradebook/teacher/main.html'
    def get_queryset(self):
        teacher = get_object_or_404(User, id=self.request.user.id)
        subject_ids = Gradebook.objects.filter(teacher=teacher).values('subject_id')
        queryset = Subject.objects.filter(id__in=subject_ids).order_by('subject')
        return queryset

class SubjectAddView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher/subject_form.html'
    form_class = SubjectForm
    def get_success_url(self):
        return reverse('teacher_main', args=[self.request.user.slug])
    def form_valid(self, form):
        subject = Subject.objects.get_or_create(title=form.cleaned_data['subject'])[0]
        teacher = get_object_or_404(User, id=self.request.user.id)
        if not Gradebook.objects.filter(teacher=teacher, subject=subject).exists():
            Gradebook.objects.create(teacher=teacher, subject=subject)
        return super().form_valid(form)

@login_required
def subject_update(request, pk, **kwargs):
    subject = get_object_or_404(Subject, pk=pk)
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            new_subject = Subject.objects.get_or_create(subject=form.cleaned_data['subject'])[0]
            
            subject_record = Gradebook.objects.filter(subject=subject, teacher=teacher)
            subject_record.update(title=new_subject)
        return redirect(reverse('teacher_main', args=[request.user.slug]))
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'gradebook/teacher/subject_form.html', {'form': form})


@login_required
def subject_delete(request, pk, **kwargs):
    subject = get_object_or_404(Subject, pk=pk)
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        subject_records = Gradebook.objects.filter(subject=subject, teacher=teacher)
        subject_records.delete()
        return redirect(reverse('teacher_main', args=[request.user.slug]))
    return render(request, 'gradebook/teacher/subject_confirm_delete.html', {'subject': subject})


@login_required
def course_add(request, **kwargs):
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == "POST":
        form = TeacherCourseForm(request.user, request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course = Course.objects.get_or_create(
            year=form.cleaned_data['year'],
            group=form.cleaned_data['group'],
            faculty=form.cleaned_data['faculty']
            )[0]
            subject = Subject.objects.get(title=form.cleaned_data['subject'])
    
            try:
                course_record = Gradebook.objects.get(teacher=teacher, subject=subject, course=None)
                course_record.course = course  
            except:
                course_record = Gradebook.objects.get_or_create(subject=subject, teacher=teacher, course=course)[0]           
            course_record.save()
            form.save_m2m()     
        return redirect(reverse('teacher_main', args=[request.user.slug]))
    else:
        form = TeacherCourseForm(request.user)
    return render(request, 'gradebook/teacher/course_form.html', {'form': form})

@login_required
def course_update(request, subject_pk, course_pk, **kwargs):
    course = get_object_or_404(Course, pk=course_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            new_course = Course.objects.get_or_create(
                faculty=form.cleaned_data['faculty'],
                year = form.cleaned_data['year'],
                group = form.cleaned_data['group'],
                )[0]
            
            course_record = Gradebook.objects.filter(course=course, subject=subject, teacher=teacher)
            course_record.update(course=new_course)
        return redirect(reverse('teacher_main', args=[request.user.slug]))
    else:
        form = CourseForm(instance=course)
    return render(request, 'gradebook/teacher/course_update.html', {'form': form, 'subject': subject})

@login_required
def course_delete(request, subject_pk, course_pk, **kwargs):
    course = get_object_or_404(Course, pk=course_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    teacher = get_object_or_404(User, id=request.user.id)
    
    if request.method == 'POST':
        Gradebook.objects.filter(course=course, subject=subject, teacher=teacher).delete()
        return redirect(reverse('teacher_main', args=[request.user.slug]))
    return render(request, 'gradebook/teacher/course_confirm_delete.html', {'course': course, 'subject': subject})


class StudentListView(LoginRequiredMixin, View):
    template_name = 'gradebook/teacher/student_list.html'
    def get(self, request, course_pk):
        course = get_object_or_404(Course, pk=course_pk)
        student_list = User.objects.filter(course=course).order_by('last_name')
        return render(request, self.template_name, {'student_list': student_list, 'course': course})

@login_required
def student_edit(request, course_pk, **kwargs):
    StudentFormSet = modelformset_factory(User, fields=('first_name', 'last_name', 'email'), extra=10,) 
    course = get_object_or_404(Course, pk=course_pk)
    
    if request.method == 'POST':
        formset = StudentFormSet(request.POST, queryset=User.objects.filter(course=course_pk))
        if formset.is_valid():
            students = formset.save(commit=False)
            for student in students:
                student.course = course
                first_name = student.first_name
                last_name = student.last_name
                student.slug = slugify(f'{first_name, last_name}')
                student.save()
                
            return redirect(reverse('teacher:student_edit', kwargs={'slug': request.user.slug, 'course_pk': course_pk}))
    else:
        formset = StudentFormSet(queryset=User.objects.filter(course=course))
    return render(request,'gradebook/teacher/student_formset.html', {'formset': formset, 'course': course})

@login_required
def student_delete(request, course_pk, student_pk, **kwargs):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(User, pk=student_pk)
    if request.method == 'POST':
        User.objects.filter(course=course, pk=student_pk).delete()
        return redirect(reverse('teacher:student_edit', kwargs={'slug': request.user.slug, 'course_pk': course_pk}))
    context = {'course':course, 'student': student}
    return render(request, 'gradebook/teacher/student_confirm_delete.html', context)



@login_required
def gradebook(request, subject_pk, course_pk, **kwargs):
    course = get_object_or_404(Course, pk=course_pk)
    subject = get_object_or_404(Subject, pk=subject_pk)
    teacher = get_object_or_404(User, pk=request.user.id)
    student_list = User.objects.filter(course=course).order_by('last_name')
    tasks_ids = Gradebook.objects.filter(course=course, subject=subject).values('task_id')
    task_list = Task.objects.filter(id__in=tasks_ids)

    if request.method == 'POST':
        task_form = TaskForm(request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            Task.title = task
            task.save()

            try:
                gb_record = Gradebook.objects.get(course=course, subject=subject, teacher=teacher, task=None)
                gb_record.task = task
            except:
                gb_record = Gradebook.objects.create(
                    course=course, subject=subject, teacher=teacher, task=task
                    )
            gb_record.save()
            kwargs = {'slug': request.user.slug, 'subject_pk': subject_pk, 'course_pk': course_pk}
            return redirect(reverse('teacher:gradebook', kwargs))

    else:
        task_form = TaskForm()
        
    ctx = {'student_list': student_list, 'course': course, 'subject': subject, 'task_form': task_form,
        'task_list': task_list
    }
    return render(request, 'gradebook/teacher/gradebook_table.html', ctx)

