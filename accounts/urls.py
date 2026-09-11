from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),

    path('employees/', views.employee_list, name='employees_list'),
    path('employees/create/', views.employee_create, name='employees_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employees_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employees_delete'),
    path('employees/users/', views.users_list, name='users_list'),
    path('employees/users/<int:pk>/toggle/', views.user_toggle_role, name='users_toggle'),
]