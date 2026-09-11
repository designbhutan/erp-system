from django.urls import path
from . import views

urlpatterns = [
    path('approvals/', views.approval_center, name='approval_center'),
]