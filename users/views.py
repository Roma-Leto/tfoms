import logging
from pyexpat.errors import messages

from django.contrib.auth.views import LoginView, LogoutView
from django.core.files.uploadedfile import UploadedFile
from django.db.models.expressions import result, Subquery
from django.utils.timezone import now
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from invoice.forms import UploadFileForm
from x_tfoms_project.celery import debug_task
from django.contrib.auth.decorators import login_required
from openpyxl import load_workbook
from django.shortcuts import render, redirect
from django.db import IntegrityError

from invoice.models import InvoiceDNRDetails, RegisterTerritorial, FileUpload, InvoiceInvoiceJobs
from invoice.views import parse_first_sheet, convert_date, mouth_converter

logger = logging.getLogger(__name__)


class TLoginView(LoginView):
    template_name = 'registration/login.html'

@login_required
def profile(request):
    logger.info("func profile")
    # debug_task.delay()  # Тест работы Celery

    # # Шаг 1: Находим пять наибольших уникальных значений цены
    # top_5_index = InvoiceInvoiceJobs.objects.values('ext_id').distinct().order_by('-ext_id')[:5]
    #
    # # Шаг 2: Используем Subquery, чтобы выбрать все строки с этими ценами
    # top_index = InvoiceInvoiceJobs.objects.filter(ext_id__in=Subquery(top_5_index.values('ext_id')))

    # Вывод результатов
    message = ''
    if request.method == 'POST':
        logger.info("func profile, method POST")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']



            # Получаем файл из формы
            uploaded_file = FileUpload(file=file)


            # Загрузка Excel-файла с помощью openpyxl
            workbook = load_workbook(file, data_only=True)
            sheet_list = list()  # Список листов

            # Итерируемся по всем листам
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]  # Получаем лист по имени
                sheet_list.append(sheet)
                logger.info(f'Название листа: {sheet_name}')  # Выводим имя листа

            # Извлекаем данные первого листа
            # итерируем по строкам листа
            data_excel = list()
            row_number = 0
            for row in sheet_list[0].iter_rows(values_only=True):
                data_excel.append(row)
                row_number += 1
            # Извлекаем данные из ячеек документа и формируем словарь
            clear_data = parse_first_sheet(data_excel, file)
            code_from_register = RegisterTerritorial.objects.get(
                code=clear_data['code_fund'])
            # Создание записи первой страницы в БД
            try:
                inv_object = InvoiceDNRDetails.objects.create(
                    file_name=file,
                    # Передаём месяц в виде числа используя функцию конвертации
                    mouth_of_invoice_receipt=mouth_converter(
                        clear_data['mouth_of_invoice_receipt']),
                    year_of_invoice_receipt=clear_data['year_of_invoice_receipt'],
                    # Преобразование даты в формат YYYY-MM-DD
                    date_of_reporting_period=convert_date(
                        clear_data['date_of_reporting_period']),
                    code_fund=code_from_register,
                    invoice_number=clear_data['invoice_number'],
                    total_amount=clear_data['total_amount'],
                    # ext_id=clear_data['ext_id']
                )
                # Сохранение файла под номером счёта
                # uploaded_file.save()
                logger.info("func profile. Сохранение данных первой страницы - ОК")
            except IntegrityError as e:
                inv_object = InvoiceDNRDetails.objects.get(invoice_number=
                                                           clear_data['invoice_number'])
                logger.error(f"Ошибка: {e}")

            item = inv_object
            # Создаем объект модели и сохраняем файл
            # Сохранение записи о файле
            try:
                uploaded_file = FileUpload(parent=item, file=file)
                file_name = uploaded_file.save()
                # uploaded_file = form.cleaned_data['file']
                # file_name = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
                # file_path = default_storage.path(file_name)
                FileUpload.objects.create(
                    uploaded_at=now(),
                    file=file_name,
                    # parent_id=item.id
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


