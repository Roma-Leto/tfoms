import logging
import re

from openpyxl import load_workbook
# from django.shortcuts import render
from django.http import HttpResponseRedirect
from datetime import datetime
from django.db import IntegrityError
from utilities import timer

from django.shortcuts import render, redirect
# from .forms import TestUploadFileForm
# from invoice.tasks import process_file

from .forms import UploadFileForm
from .models import InvoiceDNRDetails, InvoiceAttachment, RegisterTerritorial

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

def find_medical_docktor_code(lst: list):
    numbers = []

    for item in lst:
        try:
            num = int(item)  # Сначала попробуем преобразовать в целое число
            numbers.append(num)
        except ValueError:
            try:
                num = float(item)  # Затем попробуем преобразовать в вещественное число
                numbers.append(num)
            except ValueError:
                continue  # Если не получилось ни то, ни другое, пропускаем элемент

        if len(numbers) >= 2:
            break  # Останавливаемся, как только нашли два числа

    return numbers

@timer
def parse_sheet(number_sheet, data_excel):
    """
    Функция парсинга excel-файла
    :param number_sheet: номер страницы документа начиная с 0 (нуля)
    :param data_excel: кортеж данных, извлечённых со страницы документа
    :return: словарь result
    """
    invoice_number = code_fund = mouth_of_invoice_receipt = \
        year_of_invoice_receipt = date_of_reporting_period = total_amount = None
    result = dict()

    if number_sheet == 0:
        try:
            # Проверка данных перед обработкой
            if len(data_excel) > 0 and len(data_excel[0]) > 3:
                result['invoice_number'] = data_excel[0][3].split(' ')[2]
                logger.info(f"№ счёта {result['invoice_number']}")

            if len(data_excel) > 4 and len(data_excel[4]) > 3:
                result['mouth_of_invoice_receipt'] = data_excel[4][3].split(' ')[1]
                logger.info(f"Месяц {result['mouth_of_invoice_receipt']}")

                result['year_of_invoice_receipt'] = data_excel[4][3].split(' ')[2]
                logger.info(f"Год {result['year_of_invoice_receipt']}")

            postfix = '000'
            if len(data_excel) > 21 and len(data_excel[21]) > 0:
                # Выбираем первые 2 символа из строки и присоединяем три нуля в конце
                result['code_fund'] = int(list(data_excel[21][-1])[0]
                                          + list(data_excel[21][-1])[1]
                                          + postfix)
                logger.info(f"Код ТФ {result['code_fund']}")

            if len(data_excel) > 19 and len(data_excel[19]) > 0:
                result['date_of_reporting_period'] = data_excel[19][-1]
                logger.info(f"Дата счёта {result['date_of_reporting_period']}")

            if len(data_excel) > 23 and len(data_excel[23]) > 2:
                result['total_amount'] = data_excel[23][2]
                logger.info(f"Сумма счёта {result['total_amount']}")

        except IndexError as e:
            logger.error(f"Ошибка при обработке данных: {e}")

        # Обработка второго листа документа
    if number_sheet == 1:
        try:
            # Проверка данных перед обработкой
            print("data_excel", data_excel)
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

                delimiters = r'[()]'  # Символы-разделители
                result['medical_care_profile_code'] = \
                    find_medical_docktor_code(re.split(delimiters, data_excel[7]))[0]
                # logger.info(f"Код профиля медицинской помощи "
                #             f"{result['medical_care_profile_code']}")

                result['doctors_specialty_code'] = \
                    find_medical_docktor_code(re.split(delimiters, data_excel[7]))[1]
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


def convert_date(report_date_str):
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
            logger.info(f"Имя файла {file}")

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
                # logger.info(f"Данные {row_number}: {row}")

            # Извлекаем данные из ячеек документа и формируем словарь
            clear_data = parse_sheet(0, data_excel)
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
                    total_amount=clear_data['total_amount']
                )
            except IntegrityError as e:
                inv_object = InvoiceDNRDetails.objects.get(invoice_number=
                                                           clear_data['invoice_number'])
                logger.error(f"Ошибка: {e}")


            context = {
                "any_text": "Run"
            }


            # Извлекаем данные второго листа
            # итерируем по строкам листа
            data_excel = list()
            row_number = 0
            # Пропустим первые три строки
            start_row_index = 6  # Начинаем с 4-й строки (индексация с нуля)
            dataset = list()  # Список списков всех пациентов
            for row in sheet_list[1].iter_rows(min_row=start_row_index,
                                               values_only=True):

                if not None in row and not 'Х' in row:
                    data_excel.append(row)
                # if row[5] is not None and len(row[5]) > 15:
                #     row_number += 1
                    # logger.info(f"Данные {row_number}: {row}")
            # print(" data_excel.append ", data_excel)
            # Извлечение данных по каждому пациенту в БД
            for pers in data_excel:
                # Извлекаем данные из ячеек документа и формируем словарь
                clear_data = parse_sheet(1, pers)
                # print("Словари: ", clear_data)
                # Запись в БД
                InvoiceAttachment.objects.create(
                    invoice=inv_object,
                    conditions_of_medical_care=clear_data['conditions_of_medical_care'],
                    patients_name=clear_data['patients_name'],
                    birthday=convert_date(clear_data['birthday']),
                    policy_number=int(clear_data['policy_number']),
                    medical_care_profile_code=clear_data['medical_care_profile_code'],
                    doctors_specialty_code=clear_data['doctors_specialty_code'],
                    diagnosis=clear_data['diagnosis'],
                    start_date_of_treatment=convert_date(clear_data['start_date_of_treatment']),
                    end_date_of_treatment=convert_date(clear_data['end_date_of_treatment']),
                    treatment_result_code=clear_data['treatment_result_code'],
                    treatment_result_name=clear_data['treatment_result_name'],
                    volume_of_medical_care=clear_data['volume_of_medical_care'],
                    tariff=clear_data['tariff'],
                    expenses=clear_data['expenses']
                )


            # Создание записей в базе данных


            # Перенаправление после успешной загрузки
            return HttpResponseRedirect('/upload_success/')
    else:
        form = UploadFileForm()
        context = {
            'form': form,
            'any_text': 'start'
        }
    return render(request, 'invoice/upload.html', context=context)



#
# def test_view(request):
#     if request.method == 'POST':
#         form = TestUploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']
#             task_id = process_file.delay(file.read())
#             return redirect(f'/progress/{task_id}')
#     else:
#         form = UploadFileForm()
#     return render(request, 'invoice/upload.html', {'form': form})

# TODO: валидация данных
# TODO: обработка ошибок
# TODO: асинхронная обработка с помощью CELERY
