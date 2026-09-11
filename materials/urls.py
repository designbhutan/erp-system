from django.urls import path
from . import views

urlpatterns = [
    path('materials/', views.material_list, name='materials_list'),
    path('materials/request/', views.request_create, name='materials_request'),
    path('materials/my-requests/', views.my_requests, name='materials_my_requests'),
    path('materials/cancel/<int:pk>/', views.request_cancel, name='materials_cancel'),
    path('materials/pending/', views.pending_requests, name='materials_pending'),
    path('materials/review/<int:pk>/<str:action>/', views.review_request, name='materials_review'),
]