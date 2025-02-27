# region Imports
import logging
import re, os

from OpenSSL.rand import status
from celery import shared_task

from openpyxl import load_workbook
from django.shortcuts import redirect
from datetime import datetime
from django.db import IntegrityError
from utilities import timer
from x_tfoms_project import settings
from .models import InvoiceDNRDetails, InvoiceAttachment, InvoiceInvoiceJobs, InvoiceInvoiceJobSteps

# endregion Imports
logger = logging.getLogger(__name__)


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
            result['conditions_of_medical_care'] = data_excel[0]
            # logger.info(f"Кода вида и условий оказания медицинской помощи "
            #             f"{result['conditions_of_medical_care']}")
            result['usl_ok'] = 5 - int(data_excel[0][0])
            result['mocod'] = data_excel[2]
            result['tip'] = data_excel[3]
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
            result['subj_n'] = data_excel[6]
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


def find_medical_docktor_code(lst: list):
    """
    Ищет в профиле оказания медицинской помощи - специальности врача цифровые коды
    :param lst:
    :return:
    """
    numbers = []
    names = []
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
    return numbers, names


@shared_task
def celery_save_second_sheet():
    """
    Парсинг и сохранения данных второго листа отчёта
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

    # Установка флага записи в БД
    obj = InvoiceInvoiceJobs.objects.create(
        ext_id=item.id,
        step_id=1,
        ready=0,
        status="Выполняется"
    )

    # Извлечение данных по каждому пациенту в БД
    count = 0
    for pers in data_excel:
        # Извлекаем данные из ячеек документа и формируем словарь
        clear_data = parse_second_sheet(pers)
        count += 1
        # Запись в БД
        try:
            InvoiceAttachment.objects.create(
                ext_id=InvoiceDNRDetails.objects.latest('id').id,
                usl_ok=clear_data['usl_ok'],
                mocod=clear_data['mocod'],
                tip=clear_data['tip'],
                row_id=clear_data['conditions_of_medical_care'],
                fio=clear_data['patients_name'],
                dr=convert_date(clear_data['birthday']),
                enp=int(clear_data['policy_number']),
                profil_id=clear_data['medical_care_profile_code'],
                spec_id=clear_data['doctors_specialty_code'],
                profil_n=clear_data['medical_care_profile_name'],
                spec_n=clear_data['doctors_specialty_name'],
                subj_n=clear_data['subj_n'],
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
    obj.ready = 1
    obj.status = "Выполнено"
    obj.save()
    return 0
