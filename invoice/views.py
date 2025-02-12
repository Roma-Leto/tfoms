# region Imports
import logging
import re, os
import uuid

from django.views.generic import UpdateView, FormView
from openpyxl import load_workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from datetime import datetime
from django.db import IntegrityError, connection
from pandas.conftest import names

from utilities import timer
from x_tfoms_project import settings

from .forms import UploadFileForm, DNRDetailsForm
from .models import InvoiceDNRDetails, InvoiceAttachment, RegisterTerritorial, FileUpload

# endregion Utilities
logger = logging.getLogger(__name__)


# region Utilities
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


def find_medical_docktor_code(lst: list):
    """
    Ищет в профиле оказания медицинской помощи - специальности врача цифровые коды
    :param lst:
    :return:
    """
    numbers = []
    names = []
    logger.info(f"Данные find_medical_docktor_code - {lst}")
    for item in lst:
        try:
            num = int(item)  # Сначала попробуем преобразовать в целое число
            numbers.append(num)
        except ValueError:
            try:
                num = float(item)  # Затем попробуем преобразовать в вещественное число
                numbers.append(num)
            except ValueError:
                if len(item) > 2:
                    names.append(item)
                continue  # Если не получилось ни то, ни другое, пропускаем элемент

        if len(numbers) >= 2 and len(names) >= 2:
            break  # Останавливаемся, как только нашли два числа
    print("NUMBERS: ", numbers, names)
    return numbers, names


@timer
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


@timer
def parse_second_sheet(data_excel):
    """
    Функция парсинга excel-файла
    :param data_excel: кортеж данных, извлечённых со страницы документа
    :return: словарь result
    """
    result = dict()

    try:
        # Проверка данных перед обработкой
        # print("data_excel", data_excel)
        # if len(data_excel) > 0 and len(data_excel[0]) > 14:
        if True:
            result['conditions_of_medical_care'] = data_excel[0].split('.')[0]
            # logger.info(f"Кода вида и условий оказания медицинской помощи "
            #             f"{result['conditions_of_medical_care']}")
            result['patients_name'] = data_excel[1]
            # logger.info(f"ФИО {result['patients_name']}")
            result['birthday'] = data_excel[4]
            # logger.info(f"Дата рождения {result['birthday']}")
            result['policy_number'] = data_excel[5]
            # logger.info(f"Номер полиса(ЕНП) {result['policy_number']}")
            delimiters = r'[()-]'  # Символы-разделители
            result['medical_care_profile_code'] = \
                find_medical_docktor_code(re.split(delimiters, data_excel[7]))[0][0]
            # logger.info(f"Код профиля медицинской помощи "
            #             f"{result['medical_care_profile_code']}")
            result['doctors_specialty_code'] = \
                find_medical_docktor_code(re.split(delimiters, data_excel[7]))[0][1]
            # logger.info(f"Код специальности врача "
            #             f"{result['doctors_specialty_code']}")

            result['medical_care_profile_name'] = \
                find_medical_docktor_code(re.split(delimiters, data_excel[7]))[1][0]
            # logger.info(f"Код профиля медицинской помощи "
            #             f"{result['medical_care_profile_code']}")
            result['doctors_specialty_name'] = \
                find_medical_docktor_code(re.split(delimiters, data_excel[7]))[1][1]
            # logger.info(f"Код специальности врача "
            #             f"{result['doctors_specialty_code']}")


            result['diagnosis'] = data_excel[8]
            # logger.info(f"Диагноз {result['diagnosis']}")
            result['start_date_of_treatment'] = data_excel[9]
            # logger.info(f"Дата начала лечения {result['start_date_of_treatment']}")
            result['end_date_of_treatment'] = data_excel[10]
            # logger.info(f"Дата окончания лечения {result['end_date_of_treatment']}")
            result['treatment_result_code'] = \
                re.split(delimiters, data_excel[11])[1]
            # logger.info(f"Дата окончания лечения {result['treatment_result_code']}")
            result['treatment_result_name'] = \
                re.split(delimiters, data_excel[11])[2]
            # logger.info(f"Дата окончания лечения {result['treatment_result_name']}")
            result['volume_of_medical_care'] = data_excel[12]
            # logger.info(
            # f"Объёма медицинской помощи {result['volume_of_medical_care']}")
            result['tariff'] = data_excel[12]
            # logger.info(f"Тариф {result['tariff']}")
            result['expenses'] = data_excel[14]
            # logger.info(f"Расходы {result['expenses']}")


    except IndexError as e:
        logger.error(f"Ошибка при обработке данных: {e}")

    logger.info(f"Result: {result}")

    return result


def convert_date(report_date_str) -> datetime.date:
    """
    Преобразование формата даты
    :param report_date_str: Строка в формате dd.mm.yyyy
    :return report_date: Дата в формате YYYY-MM-DD
    """
    try:
        # Преобразуем строку в объект datetime
        report_date = datetime.strptime(report_date_str, "%d.%m.%Y").date()
        return report_date
    except ValueError as e:
        print(f"Неверный формат даты: {e}")
        return False


# endregion Utilities

@timer
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
        form = UploadFileForm()

    return render(request, 'invoice/upload.html', {'form': form})


def upload_second_sheet(request):
    """
    Парсинг и сохранения данных второго листа отчёта
    :param request:
    :return:
    """
    # region Поиск и загрузка файла счёта в память
    item = InvoiceDNRDetails.objects.latest('id')
    filename = item.file_name.replace(' — ',
                                      '__')  # замена длинного тире на обычный дефис
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
    # endregion Поиск и загрузка файла счёта в память

    # region Проверка открытия файла отчёта
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    try:
        workbook = load_workbook(file_path, data_only=True)
    except Exception as e:
        logger.info(f"Произошла ошибка при открытии файла: {e}")
    # endregion Проверка открытия файла отчёта

    # region Формируем список листов
    # Загрузка Excel-файла с помощью openpyxl
    workbook = load_workbook(file_path, data_only=True)
    sheet_list = list()
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]  # Получаем лист по имени
        sheet_list.append(sheet)
        logger.info(f'Название листа: {sheet_name}')  # Выводим имя листа
    # endregion Формируем список листов

    # region Сохраняем каждую строку данных в базу данных
    data_excel = list()  # Создаём список для строк документа
    # Пропустим первые три строки
    start_row_index = 6  # Начинаем с 4-й строки (индексация с нуля)
    for row in sheet_list[1].iter_rows(min_row=start_row_index,
                                       values_only=True):
        if not None in row and not 'Х' in row:
            data_excel.append(row)
    # Извлечение данных по каждому пациенту в БД
    for pers in data_excel:
        # Извлекаем данные из ячеек документа и формируем словарь
        clear_data = parse_second_sheet(pers)
        print("Словари: ", clear_data)
        # Запись в БД
        try:
            InvoiceAttachment.objects.create(
                ext_id=InvoiceDNRDetails.objects.latest('id').id,
                row_id=clear_data['conditions_of_medical_care'],
                fio=clear_data['patients_name'],
                dr=convert_date(clear_data['birthday']),
                enp=int(clear_data['policy_number']),
                profil_id=clear_data['medical_care_profile_code'],
                spec_id=clear_data['doctors_specialty_code'],
                profil_n=clear_data['medical_care_profile_name'],
                spec_n=clear_data['doctors_specialty_name'],
                dz=clear_data['diagnosis'],
                date1=convert_date(
                    clear_data['start_date_of_treatment']),
                date2=convert_date(
                    clear_data['end_date_of_treatment']),
                rslt_id=clear_data['treatment_result_code'],
                rslt_n=clear_data['treatment_result_name'],
                cnt_usl=clear_data['volume_of_medical_care'],
                tarif=clear_data['tariff'],
                sum_usl=clear_data['expenses']
            )
        except IntegrityError as e:
            logger.info(f"Запись с такими параметрами уже существует. {e}")
    # endregion Сохраняем каждую строку данных в базу данных

    context = {
        'data': "result data"
    }

    return render(request, 'invoice/data_processing_result.html', context)


class DataUpdate(UpdateView):
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


from django.shortcuts import render



from django.http import HttpResponse
from django.db import connection

def hello_world_view(request):
    """Тестовая функция вызова процедуры из БД"""
    ver = 3
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
        print('ver = 2')
        with connection.cursor() as cursor:
            output_message = cursor.fetchone(str)
            try:
                cursor.execute("EXEC dbo.hello_world")
                result = cursor.fetchone()
                message = result[
                    0] if result else "Процедура выполнена, но ничего не вернула."
            except Exception as e:
                message = f"Произошла ошибка при выполнении процедуры: {e}"
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