from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.company_reports, name='reports_company'),
    path('reports/my/', views.my_reports, name='reports_my'),
]