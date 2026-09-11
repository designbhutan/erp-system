from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('leave.urls')),
    path('', include('materials.urls')),
    path('', include('vehicles.urls')),
    path('', include('approvals.urls')),
    path('', include('procurement.urls')),
    path('', include('reports.urls')),
    path('', include('core.urls')),
]