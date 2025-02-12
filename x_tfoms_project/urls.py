"""
URL configuration for x_tfoms_project project.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from invoice.views import upload_file, DataUpdate, upload_second_sheet
import invoice.views as views
urlpatterns = [
    path('admin/', admin.site.urls),

    path('up/save_second/', upload_second_sheet, name='save_second'),
    path('up/<int:pk>', DataUpdate.as_view(), name='edit-book'),
    path('upload_success/', TemplateView.as_view(template_name='invoice/upload_success.html'), name='upload_success'),
    path('', upload_file, name='upload_file'),
    path('data_processing_result', upload_file, name='upload_file'),

    path('hello-world/', views.hello_world_view, name='hello_world'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
