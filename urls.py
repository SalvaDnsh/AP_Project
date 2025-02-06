from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLogoutView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('filter_courses/', views.filter_courses, name='filter_courses'),
    path('toggle_course_selection/', views.toggle_course_selection, name='toggle_course_selection'),
    path('get_selected_credits/', views.get_selected_credits, name='get_selected_credits'),
    path('weekly_schedule/', views.weekly_schedule, name='weekly_schedule'),
    path('login/', views.login_view, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('check_selected_course/', views.check_selected_course, name='check_selected_course'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_course/', views.add_course, name='add_course'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage_courses/', views.manage_courses, name='manage_courses'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('reset_password/', views.reset_password, name='password_reset'),
    path('change_password/', views.change_password, name='change_password'),
    path('add_user/', views.add_user, name='add_user'),


]
