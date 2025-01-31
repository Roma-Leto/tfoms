"""
URL configuration for x_tfoms_project project.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from invoice.views import upload_file

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('upload_success/', TemplateView.as_view(template_name='invoice/upload_success.html'), name='upload_success'),
    path('admin/', admin.site.urls),
]
