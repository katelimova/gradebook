from django.contrib.auth import login, authenticate
from django.forms.formsets import BaseFormSet, formset_factory
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.forms import modelformset_factory, formset_factory
from django.urls import reverse
from django.views.generic import View, ListView, DetailView, TemplateView, UpdateView, CreateView
from django.views.generic.edit import DeleteView, FormView
from gradebook.forms import TaskForm, RegistrationForm, SubjectForm, TeacherCourseForm, CourseForm, GradeForm
from gradebook.models import Task, Course, Subject, User, Gradebook
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.template.defaultfilters import slugify
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
        queryset = Subject.objects.filter(id__in=subject_ids).order_by('title')
        return queryset

class SubjectAddView(LoginRequiredMixin, FormView):
    template_name = 'gradebook/teacher/subject_form.html'
    form_class = SubjectForm
    def get_success_url(self):
        return reverse('teacher_main', args=[self.request.user.slug])
    def form_valid(self, form):
        subject = Subject.objects.get_or_create(title=form.cleaned_data['title'])[0]
        teacher = get_object_or_404(User, id=self.request.user.id)
        Gradebook.objects.get_or_create(teacher=teacher, subject=subject)
        return super().form_valid(form)

@login_required
def subject_update(request, pk, **kwargs):
    subject = get_object_or_404(Subject, pk=pk)
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            new_subject = Subject.objects.get_or_create(title=form.cleaned_data['title'])[0]
            
            Gradebook.objects.filter(subject=subject, teacher=teacher).update(subject=new_subject)

        return redirect(reverse('teacher_main', args=[request.user.slug]))
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'gradebook/teacher/subject_form.html', {'form': form})


@login_required
def subject_delete(request, pk, **kwargs):
    subject = get_object_or_404(Subject, pk=pk)
    teacher = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        Gradebook.objects.filter(subject=subject, teacher=teacher).delete()
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
                faculty=form.cleaned_data['faculty'],
            )[0]
            subject = Subject.objects.get(title=form.cleaned_data['subject'])

            Gradebook.objects.update_or_create(
                teacher=teacher, subject=subject, course=None,
                defaults={'course':course},
            )
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
            
            Gradebook.objects.filter(course=course, subject=subject, teacher=teacher).update(course=new_course)
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


# class StudentListView(LoginRequiredMixin, View):
#     template_name = 'gradebook/teacher/student_list.html'
#     def get(self, request, course_pk):
#         course = get_object_or_404(Course, pk=course_pk)
#         student_list = User.objects.filter(course=course).order_by('last_name')
#         return render(request, self.template_name, {'student_list': student_list, 'course': course})

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
                Gradebook.objects.create(course=course, student=student)

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

    task_form=TaskForm()
    GradeFormSet = modelformset_factory(Gradebook, fields=(
        'grade', 'student', 'task',), max_num=len(student_list), extra=7,
    )

    if request.method == 'POST':

        if 'add_task' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.save()
                
                Gradebook.objects.update_or_create(
                    course=course, subject=subject, teacher=teacher, task=None,
                    defaults={'task': task},
                )

            return redirect(reverse('teacher:gradebook', 
                    kwargs={'slug': request.user.slug, 'subject_pk': subject_pk, 'course_pk': course_pk})
                )

        elif 'add_grade' in request.POST:
            grade_formset = GradeFormSet(request.POST, queryset=None)
            if grade_formset.is_valid():
                formset = grade_formset.save(commit=False)
                for form in formset:

                    stud_record = Gradebook.objects.filter(
                        course=course, subject=subject, teacher=teacher, task=form.task, student=form.student)
                    if stud_record.exists():
                            stud_record.update(grade=form.grade)
                    else:
                        Gradebook.objects.filter(
                            course=course, subject=subject, teacher=teacher, task=form.task,
                        ).update(grade=form.grade, student=form.student)

                return redirect(reverse('teacher:gradebook', 
                    kwargs={'slug': request.user.slug, 'subject_pk': subject_pk, 'course_pk': course_pk})
                )

    else:
        task_form = TaskForm()
        GradeFormSet = formset_factory(GradeForm,
            extra=(len(task_list)*len(student_list)),
        )
        grade_formset = GradeFormSet()
        
    ctx = {'student_list': student_list, 'course': course, 'subject': subject, 'task_form': task_form,
        'task_list': task_list, 'formset': grade_formset,
    }
    return render(request, 'gradebook/teacher/gradebook_table.html', ctx)

