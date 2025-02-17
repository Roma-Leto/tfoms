from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views import View

from invoice.forms import UploadFileForm
from invoice.models import InvoiceDNRDetails
# region Imports
import logging
import re, os
import uuid

from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, FormView
from openpyxl import load_workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from datetime import datetime
from django.db import IntegrityError, connection
from pandas.conftest import names

from utilities import timer
from x_tfoms_project import settings

# from .forms import UploadFileForm, DNRDetailsForm
from invoice.models import (InvoiceDNRDetails, InvoiceAttachment, RegisterTerritorial,
                            FileUpload)
from invoice.views import (parse_first_sheet, parse_second_sheet, convert_date,
                           find_medical_docktor_code, mouth_converter)

logger = logging.getLogger(__name__)


class TLoginView(LoginView):
    template_name = 'registration/login.html'

@login_required
def profile(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            uploaded_file = FileUpload(file=file)
            uploaded_file.save()
            logger.info(f"Имя файла {file}. Сохранено")

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
            except IntegrityError as e:
                inv_object = InvoiceDNRDetails.objects.get(invoice_number=
                                                           clear_data['invoice_number'])
                logger.error(f"Ошибка: {e}")

            form = InvoiceDNRDetails(request.POST)
            item = inv_object

            # Перенаправление после успешной загрузки
            return render(request, 'invoice/upload_success.html',
                          {
                              'form': form,
                              'pk': item.id
                          })
    else:
        invoice_list = InvoiceDNRDetails.objects.all()
        form = UploadFileForm()
        context = {
            'invoices': invoice_list,
            'form': form
        }
    return render(request, 'registration/profile.html', context=context)