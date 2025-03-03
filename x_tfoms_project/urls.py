"""
URL configuration for x_tfoms_project project.
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from invoice.views import upload_file, DataUpdate, upload_second_sheet
from users.views import TLoginView, profile
import invoice.views as views
urlpatterns = [
    path('admin/', admin.site.urls),

    path('up/save_second/', upload_second_sheet, name='save_second'),
    path('up/<int:pk>', DataUpdate.as_view(), name='edit-book'),
    path('upload_success/', TemplateView.as_view(template_name='invoice/upload_success.html'), name='upload_success'),
    path('upload_file/', upload_file, name='upload_file'),
    path('profile/', profile, name='profile'),
    path('', TLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('data_processing_result/', upload_file, name='upload_file'),

    path('details/<int:pk>', views.InvoiceDetail.as_view(), name='details-list'),

    path('hello-world/', views.hello_world_view, name='hello_world'),
    path('procedure_invoice/', views.check_invoice_procedure_view, name='check_invoice_procedure'),
    path('procedure_frzl/', views.check_frzl_update_procedure_view, name='check_frzl_update_procedure'),


    path('tb/', TemplateView.as_view(template_name='invoice/test_boot.html'), name='tb'),

    path('mock/', views.excel_mock, name='mock'), # удалить после отладки формирования отчёта


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
