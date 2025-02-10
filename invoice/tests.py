import os
import pytest

from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import InvoiceDNRDetails, InvoiceAttachment, FileUpload, RegisterTerritorial

# Путь к Excel-файлу
EXCEL_FILE_PATH = os.path.join(os.path.dirname(__file__), '../61_tc_24126101_test.xlsx')


# Тесты корректного открытия всех страниц
# Тест корректной загрузки файла
# Тест вьюшек


@pytest.fixture
def real_excel_file():
    """Подгружаем в окружение тестовый Excel-файл"""
    with open(EXCEL_FILE_PATH, 'rb') as f:
        return SimpleUploadedFile(f.name, f.read(),
                                  content_type='application/vnd.ms-excel')


@pytest.fixture
def register_territorial():
    """Создаём запись в модели субъектов для использования в тестовой функции"""
    return RegisterTerritorial.objects.create(code=21000,
                                              name='ДНР')


@pytest.mark.django_db
def test_real_excel_file_upload(client, real_excel_file, register_territorial):
    """Функция корректной загрузки тестовых данных и записи данных в БД"""
    url = reverse('upload_file')
    form_data = {'file': real_excel_file}
    response = client.post(url, data=form_data)

    # Проверяем успешный ответ
    assert response.status_code == 200

    # Проверяем количество записей в базе данных
    assert InvoiceDNRDetails.objects.count() > 0

    code_fund = RegisterTerritorial.objects.get(code=21000)
    print(code_fund.code)
    # Проверяем правильность данных в базе данных
    records = InvoiceDNRDetails.objects.all()
    for record in records:
        assert isinstance(record.file_name, str)
        assert isinstance(record.mouth_of_invoice_receipt, int)
        assert isinstance(record.year_of_invoice_receipt, int)
        assert isinstance(record.date_of_reporting_period, date)
        assert isinstance(record.code_fund.code, int)
        assert isinstance(record.invoice_number, int)
        assert isinstance(record.total_amount, float)
