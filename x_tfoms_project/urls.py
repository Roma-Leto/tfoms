"""
URL configuration for x_tfoms_project project.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from invoice.views import upload_file

urlpatterns = [

    path('upload_success/', TemplateView.as_view(template_name='invoice/upload_success.html'), name='upload_success'),
    path('admin/', admin.site.urls),
    path('', upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
