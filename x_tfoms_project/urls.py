"""
URL configuration for x_tfoms_project project.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from invoice.views import upload_file, get_task_progress#, long_running_view sse_view, sse_page
# from invoice.views import test_view

urlpatterns = [
    # path('sse/', sse_view, name='sse'),
    path('task/progress/<task_id>/', get_task_progress, name='task_progress'),
    # path('page/', sse_page, name='sse_page'),
    # path('page/', long_running_view, name='sse_page'),
    # path('progress/', test_view, name='test_view'),
    path('upload_success/', TemplateView.as_view(template_name='invoice/upload_success.html'), name='upload_success'),
    path('admin/', admin.site.urls),
    path('', upload_file, name='upload_file'),
]
