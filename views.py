from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Department, SelectedCourse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .forms import CourseForm, UserEditForm
from django.contrib.auth import get_user_model
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from .forms import ResetPasswordForm, ChangePasswordForm
from django.db import IntegrityError
from .models import CustomUser
import random
import string
from django.db import models



User = get_user_model()
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirect to home after logout

def course_list(request):
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', None)

    user = request.user if request.user.is_authenticated else None

    # Retrieve courses with combined capacity (filled/total format)
    courses = Course.objects.all()

    if search_query:
        courses = courses.filter(name__icontains=search_query) | courses.filter(code__icontains=search_query)
    if department_id:
        courses = courses.filter(department_id=department_id)

    selected_courses = Course.objects.filter(selectedcourse__user=user) if user else Course.objects.none()
    unselected_courses = courses.exclude(id__in=selected_courses.values_list('id', flat=True))

    # Format filled/total capacity
    for course in courses:
        course.combined_capacity = f"{course.filled_capacity}/{course.total_capacity}"

    # Group courses by department
    grouped_courses = {}
    for course in courses:
        if course.department.name not in grouped_courses:
            grouped_courses[course.department.name] = []
        grouped_courses[course.department.name].append(course)

    departments = Department.objects.all()

    return render(request, 'courses/course_list.html', {
        'departments': departments,
        'grouped_courses': grouped_courses,
        'unselected_courses': selected_courses,
        'department_id': str(department_id),
    })
def filter_courses(request):
    department_id = request.GET.get('department_id')
    courses = Course.objects.filter(department_id=department_id).values(
        'id', 'code', 'name', 'credit_hours', 'class_time',
        'exam_time', 'instructor_name', 'total_capacity', 'filled_capacity'
    )

    # Add combined capacity in the response
    for course in courses:
        course['combined_capacity'] = f"{course['filled_capacity']}/{course['total_capacity']}"

    return JsonResponse(list(courses), safe=False)

from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Course, SelectedCourse

@csrf_exempt
@login_required
def toggle_course_selection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            action = data.get('action')
            user = request.user

            print(f"Received course_id: {course_id}, action: {action}")

            course = get_object_or_404(Course, id=course_id)
            selected_courses = SelectedCourse.objects.filter(user=user)
            total_credits = sum(sc.course.credit_hours for sc in selected_courses)

            if action == 'add':
                for selected in selected_courses:
                    if selected.course.day == course.day and selected.course.class_time == course.class_time:
                        return JsonResponse(
                            {'success': False,
                             'message': 'This course overlaps in timing with one of the other courses.'})
                if SelectedCourse.objects.filter(user=user, course=course).exists():
                    return JsonResponse({'success': False, 'message': 'You have already selected this course.', 'total_credits': total_credits})

                if course.filled_capacity >= course.total_capacity:
                    return JsonResponse({'success': False, 'message': 'Course capacity is full.', 'total_credits': total_credits})

                # Prevent exceeding 20 credits
                if total_credits + course.credit_hours > 20:
                    return JsonResponse({'success': False, 'message': 'Credit limit exceeded! You can only take up to 20 credits.', 'total_credits': total_credits})

                # Add course and update filled capacity
                SelectedCourse.objects.create(user=user, course=course)
                course.filled_capacity += 1
                course.save()
                return JsonResponse({'success': True, 'message': 'Course added successfully.', 'total_credits': total_credits + course.credit_hours})

            elif action == 'remove':
                selected_course = SelectedCourse.objects.filter(user=user, course=course).first()
                if selected_course:
                    selected_course.delete()
                    course.filled_capacity -= 1
                    course.save()
                    return JsonResponse({'success': True, 'message': 'Course removed successfully.', 'total_credits': total_credits - course.credit_hours})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid request format.'})
        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Course not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def get_selected_credits(request):
    user = request.user  # Get logged-in user
    selected_courses = SelectedCourse.objects.filter(user=user)  # Fetch selected courses

    # Sum up the credit hours of selected courses
    total_credits = sum(course.course.credit_hours for course in selected_courses)

    return JsonResponse({'total_credits': total_credits})

def home(request):
    return render(request, 'home.html')

def weekly_schedule(request):
    user_id = request.user.id
    selected_courses = SelectedCourse.objects.filter(user_id=user_id)

    # Organize courses by weekdays
    weekly_schedule = {
        'Saturday': [], 'Sunday': [], 'Monday': [],
        'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []
    }

    for selected in selected_courses:
        course = selected.course
        if course.day in weekly_schedule:
            weekly_schedule[course.day].append({
                'name': course.name,
                'time': course.class_time
            })

    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    schedule_times = ['8:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00']

    return render(request, 'courses/weekly_schedule.html', {
        'weekly_schedule': weekly_schedule,
        'days': days,
        'schedule_times': schedule_times,
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check if the user is an admin (staff user)
            if user.is_staff:
                return redirect('admin_dashboard')  # Redirect admin to course management

            return redirect('course_list')  # Redirect students to the course list
        else:
            return render(request, 'courses/login.html', {'form': form, 'error': 'Invalid student ID or password.'})

    form = LoginForm()
    return render(request, 'courses/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])  # Hash password
                user.save()
                return redirect('login')  # Redirect to login after successful registration
            except IntegrityError:
                form.add_error("national_id", "This National ID is already registered.")  # Display error on form

    else:
        form = RegistrationForm()

    return render(request, 'courses/register.html', {'form': form})
# Restrict access to admins only
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)

@admin_required
def admin_dashboard(request):
    courses = Course.objects.all()
    return render(request, 'courses/admin_dashboard.html', {'courses': courses})

@admin_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/add_course.html', {'form': form})

@admin_required
def edit_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit_course.html', {'form': form})

@admin_required
def delete_course(request, course_id):
    course = Course.objects.get(id=course_id)
    course.delete()
    return redirect('admin_dashboard')

@admin_required
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'courses/manage_users.html', {'users': users})

@admin_required
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'courses/edit_user.html', {'form': form})

@admin_required
def manage_courses(request):
    search_query = request.GET.get('search', '')

    # Filter courses based on search query
    courses = Course.objects.all()
    if search_query:
        courses = courses.filter(
            models.Q(name__icontains=search_query) |
            models.Q(code__icontains=search_query) |
            models.Q(department__name__icontains=search_query)
        )

    return render(request, 'courses/manage_courses.html', {'courses': courses})

@admin_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('manage_users')


@admin_required
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'courses/edit_user.html', {'form': form})


@login_required
def check_selected_course(request):
    course_id = request.GET.get('course_id')
    user = request.user
    selected = SelectedCourse.objects.filter(user=user, course_id=course_id).exists()
    return JsonResponse({'selected': selected})


def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            national_id = form.cleaned_data['national_id']

            try:
                user = CustomUser.objects.get(email=email, national_id=national_id)

                # Generate a secure temporary password
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Set and save the new temporary password
                user.set_password(temp_password)
                user.save()

                return render(request, 'courses/reset_password.html', {
                    'form': form,
                    'temp_password': temp_password,  # Display this securely
                    'success': True
                })

            except CustomUser.DoesNotExist:
                return render(request, 'courses/reset_password.html', {
                    'form': form,
                    'error': 'Invalid National ID or Email!'
                })

    else:
        form = ResetPasswordForm()

    return render(request, 'courses/reset_password.html', {'form': form})
@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            return redirect('login')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'courses/change_password.html', {'form': form})

@admin_required
def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Hash password
            user.save()
            return redirect('manage_users')  # Redirect after adding user
    else:
        form = RegistrationForm()

    return render(request, 'courses/add_user.html', {'form': form})  # ✅ Create a new template
