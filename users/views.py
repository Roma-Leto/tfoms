import logging

from openpyxl import load_workbook
from django.contrib.auth.views import LoginView
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import IntegrityError

from x_tfoms_project.celery import debug_task
from invoice.forms import UploadFileForm
from invoice.models import InvoiceDNRDetails, RegisterTerritorial, FileUpload
from invoice.views import (parse_first_sheet, mouth_converter, region_identification,
                           save_data_from_first_sheet, save_data_from_first_sheet_lnr)
from invoice.tasks import convert_date
logger = logging.getLogger(__name__)
# TODO: обработать ситуацию отсутствия файлов для скачивания и сокрытия ссылок

class TLoginView(LoginView):
    template_name = 'registration/login.html'

@login_required
def profile(request):
    logger.info("func profile")
    # Вывод результатов
    message = ''
    if request.method == 'POST':
        logger.info("func profile, method POST")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # Загрузка Excel-файла с помощью openpyxl
            workbook = load_workbook(file, data_only=True)
            # Получаем первый лист
            first_sheet_name = workbook.sheetnames[0]
            first_sheet = workbook[first_sheet_name]

            # Логируем название первого листа
            logger.info(f'Название листа: {first_sheet_name}')

            # Извлекаем данные из первого листа
            data_excel = [row for row in first_sheet.iter_rows(values_only=True)]

            region = region_identification(data_excel)
            if region == 'Донецк':
                item = save_data_from_first_sheet_lnr(data_excel, file)
            elif region == 'Луганск':
                item = save_data_from_first_sheet_lnr(data_excel, file)

            # Сохранение файла
            try:
                uploaded_file = FileUpload(parent=item, file=file)
                file_name = uploaded_file.save()
                FileUpload.objects.create(
                    uploaded_at=now(),
                    file=file_name,
                )
                logger.info(f"Имя файла {file}. Сохранено")
            except IntegrityError as e:
                logger.info(f"Ошибка {e}")

            return redirect('edit-book', item.id)

    else:
        logger.info("func profile, method GET")
        invoice_list = InvoiceDNRDetails.objects.all()
        form = UploadFileForm()
        context = {
            'invoices': invoice_list,
            'form': form,
            'result': message,
        }
    return render(request, 'registration/profile.html', context=context)


