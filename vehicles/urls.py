from django.urls import path
from . import views

urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicles_list'),
    path('vehicles/book/', views.booking_create, name='vehicles_book'),
    path('vehicles/my-bookings/', views.my_bookings, name='vehicles_my_bookings'),
    path('vehicles/cancel/<int:pk>/', views.booking_cancel, name='vehicles_cancel'),
    path('vehicles/pending/', views.pending_bookings, name='vehicles_pending'),
    path('vehicles/review/<int:pk>/<str:action>/', views.review_booking, name='vehicles_review'),
    path('vehicles/complete/<int:pk>/', views.complete_booking, name='vehicles_complete'),
]