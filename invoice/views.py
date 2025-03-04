# region Imports
import logging
import re, os
import uuid
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, FormView, DetailView
from openpyxl import load_workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from datetime import datetime
from django.db import IntegrityError, connection
from pandas.conftest import names
from utilities import timer
from x_tfoms_project import settings
from .forms import UploadFileForm, DNRDetailsForm
from .models import InvoiceDNRDetails, InvoiceAttachment, RegisterTerritorial, FileUpload, InvoiceInvoiceJobs
from .tasks import celery_save_second_sheet, convert_date

# endregion Imports

# region Utilities
logger = logging.getLogger(__name__)


def mouth_converter(mouth: str) -> int:
    """
    Переводит название месяца в число
    :param mouth: строка с наименованием месяца
    :return: int
    """
    mouth_dict = {
        'январь': 1,
        'февраль': 2,
        'март': 3,
        'апрель': 4,
        'май': 5,
        'июнь': 6,
        'июль': 7,
        'август': 8,
        'сентябрь': 9,
        'октябрь': 10,
        'ноябрь': 11,
        'декабрь': 12,
    }

    return mouth_dict[mouth.lower()]


def parse_first_sheet(data_excel, file):
    """
    Функция парсинга excel-файла
    :param data_excel: кортеж данных, извлечённых со страницы документа
    :return: словарь result
    """
    result = dict()

    try:
        # Проверка данных перед обработкой
        if len(data_excel) > 0 and len(data_excel[0]) > 3:
            result['invoice_number'] = data_excel[0][3].split(' ')[2]

        if len(data_excel) > 4 and len(data_excel[4]) > 3:
            result['mouth_of_invoice_receipt'] = data_excel[4][3].split(' ')[1]
            result['year_of_invoice_receipt'] = data_excel[4][3].split(' ')[2]

        postfix = '000'
        if len(data_excel) > 21 and len(data_excel[21]) > 0:
            # Выбираем первые 2 символа из строки и присоединяем три нуля в конце
            result['code_fund'] = int(list(data_excel[21][-1])[0]
                                      + list(data_excel[21][-1])[1]
                                      + postfix)

        if len(data_excel) > 19 and len(data_excel[19]) > 0:
            result['date_of_reporting_period'] = data_excel[19][-1]

        if len(data_excel) > 23 and len(data_excel[23]) > 2:
            result['total_amount'] = data_excel[23][2]

        result['ext_id'] = str(uuid.uuid4())

        logger.info(
            f"\n№ счёта {result['invoice_number']}\n"
            f"Месяц {result['mouth_of_invoice_receipt']}\n"
            f"Год {result['year_of_invoice_receipt']}\n"
            f"Код ТФ {result['code_fund']}\n"
            f"Дата счёта {result['date_of_reporting_period']}\n"
            f"Сумма счёта {result['total_amount']}\n"
        )

    except IndexError as e:
        logger.error(f"Ошибка при обработке данных: {e}")
    return result


# endregion Utilities


@login_required
def upload_file(request):
    """
    Функция загрузки файла для обработки
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            uploaded_file = FileUpload(file=file)
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
            # Сохранение файла под номером счёта
            uploaded_file.save(str(clear_data['invoice_number']))
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
        form = UploadFileForm()

    return render(request, 'invoice/upload.html', {'form': form})


def upload_second_sheet(request):
    """
    Парсинг и сохранения данных второго листа отчёта
    :param request:
    :return:
    """
    logger.info('Запуск сохранения данных пациентов')
    invoice_number = request.session.get('invoice_number')

    # Очищаем сессию
    if 'invoice_number' in request.session:
        del request.session['invoice_number']

    celery_save_second_sheet.delay(invoice_number)
    logger.info('Завершение сохранения данных пациентов')
    return redirect('profile')


class DataUpdate(UpdateView, LoginRequiredMixin):
    model = InvoiceDNRDetails
    fields = ['mouth_of_invoice_receipt',
              'year_of_invoice_receipt',
              'date_of_reporting_period',
              'code_fund',
              'invoice_number',
              'total_amount'
              ]
    template_name_suffix = "_update"
    success_url = 'save_second'

    def form_valid(self, form):
        # Перехват значения invoice_number из формы
        invoice_number = form.cleaned_data['invoice_number']
        # Сохранение номера счёта для передачи в функцию обработки второго листа
        self.request.session['invoice_number'] = invoice_number
        # Вызов родительского метода для сохранения формы
        return super().form_valid(form)


class InvoiceDetail(DetailView, LoginRequiredMixin):
    model = InvoiceDNRDetails
    template_name = 'invoice/invoice_details.html'

    def get_context_object_name(self, obj):
        return 'details'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем связанные объекты
        context['items'] = InvoiceAttachment.objects.filter(ext_id=self.kwargs['pk'])
        context['jobs'] = InvoiceInvoiceJobs.objects.filter(ext_id=self.kwargs['pk'])
        # context['items'] = super().get_queryset().prefetch_related('invoice_att')
        # context["now"] = timezone.now()
        return context


# views.py

from django.http import HttpResponse, Http404
from django.conf import settings
import os

def download_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'results', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404("File not found")


def call_check_invoice_procedure(ext_id):
    with connection.cursor() as cursor:
        # Вызов хранимой процедуры с параметром
        cursor.execute("EXEC dbo.check_invoice @ext_id = %s", [ext_id])
        row = cursor.fetchone()
        print("ROW: ", row)
        #
        # if row:
        #     return row[0]  # Возвращаем сообщение
        # return None


def check_invoice_procedure_view(request):
    field_data = InvoiceDNRDetails.objects.latest('id').id
    print(field_data)
    call_check_invoice_procedure(field_data)
    now = datetime.now()
    html = '<html lang="en"><body>OK! result %s.</body></html>' % now
    return HttpResponse(html)


def call_frzl_update_procedure():
    with connection.cursor() as cursor:
        # Вызов хранимой процедуры с параметром
        cursor.execute("EXEC dbo.frzl_update")


def check_frzl_update_procedure_view(request):
    call_frzl_update_procedure()
    now = datetime.now()
    html = '<html lang="en"><body>OK! result %s.</body></html>' % now
    return HttpResponse(html)



# ----------------------VVVV тест вызова процедуры VVVV-------------------------


from django.shortcuts import render



from django.http import HttpResponse
from django.db import connection
from django.http import JsonResponse


def call_hello_world_procedure(name):
    with connection.cursor() as cursor:
        # Вызов хранимой процедуры с параметром
        cursor.execute("EXEC dbo.hello_world @name = %s", [name])
        row = cursor.fetchone()

        if row:
            return row[0]  # Возвращаем сообщение
        return None


def hello_world_view(request):
    """Тестовая функция вызова процедуры из БД"""
    ver = 2
    message = 'Что-то произошло'
    if ver == 1:
        print('ver = 1')
        with connection.cursor() as cursor:
            try:
                cursor.execute("EXEC dbo.hello_world")
                message = "Процедура выполнена успешно!"
            except Exception as e:
                message = f"Произошла ошибка при выполнении процедуры: {e}"
    elif ver == 2:
        name = request.GET.get('name',
                               'World')  # Получаем параметр 'name' из запроса, по умолчанию 'World'
        message = call_hello_world_procedure(name)
        return JsonResponse({'message': message})
    else:
        print('ver pyodbc')
        import pyodbc

        # Настройки подключения к базе данных
        server = '192.168.0.12'
        database = 'mtrnt'
        username = 'leto'
        password = '1MSLeto'
        driver = '{ODBC Driver 17 for SQL Server}'

        # Соединение с базой данных
        connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        try:
            # Выполнение процедуры
            cursor.execute("EXEC dbo.hello_world")

            # Получение результата (если процедура возвращает данные)
            message = cursor.fetchall()

            # Обработка результата
            if message:
                print(f"Результат выполнения процедуры: {message}")
            else:
                print("Процедура выполнена успешно!")

            return HttpResponse(message)
        except pyodbc.Error as e:
            print(f"Произошла ошибка при выполнении процедуры: {e}")
        finally:
            # Закрываем соединение
            cursor.close()
            conn.close()

    return HttpResponse(message)

from invoice.tasks import create_report
def excel_mock(request):
    """# удалить после отладки формирования отчёта"""
    create_report(39)
    return HttpResponse("200")