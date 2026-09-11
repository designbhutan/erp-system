from django.urls import path
from . import views

urlpatterns = [
    path('procurement/', views.po_list, name='po_list'),
    path('procurement/create/', views.po_create, name='po_create'),
    path('procurement/<int:pk>/', views.po_detail, name='po_detail'),
    path('procurement/<int:pk>/<str:action>/', views.po_action, name='po_action'),
]