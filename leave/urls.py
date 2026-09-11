from django.urls import path
from . import views

urlpatterns = [
    path('leave/', views.leave_home, name='leave_home'),
    path('leave/apply/', views.leave_apply, name='leave_apply'),
    path('leave/cancel/<int:pk>/', views.leave_cancel, name='leave_cancel'),
    path('leave/pending/', views.leave_pending, name='leave_pending'),
    path('leave/review/<int:pk>/<str:action>/', views.leave_review, name='leave_review'),
]