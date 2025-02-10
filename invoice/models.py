"""
Описание моделей базы данных для приложения обработки счетов Invoice
"""
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import models

# Данные счёта
class InvoiceDNRDetails(models.Model):
    """
    Модель базы данных для первой страница счёта в файле Excel
    """
    # Поле имени загруженного файла
    file_name = models.CharField(
        max_length=30,  # Максимум 30 символов
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Имя файла"  # Название поля
    )
    # Поле даты поступления счёта
    mouth_of_invoice_receipt = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Месяц поступления счёта"  # Название поля
    )
    # Поле даты поступления счёта
    year_of_invoice_receipt = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Год поступления счёта"  # Название поля
    )
    # Поле даты отчётного периода
    date_of_reporting_period = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата отчётного периода"  # Название поля
    )
    # Поле кода территориального фонда
    code_fund = models.ForeignKey(
    "RegisterTerritorial",
        on_delete=models.PROTECT,
        max_length=5,  # Максимум 8 символов
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Код территориального фонда"  # Название поля
    )
    # Поле номера счёта
    invoice_number = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Номер счёта",  # Название поля
        unique=True  # Уникальное поле
    )
    # Поле суммы счёта
    total_amount = models.FloatField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Сумма счёта"  # Название поля
    )

    class Meta:
        pass

    def __str__(self):
        return self.invoice_number

# Записи пациентов
class InvoiceAttachment(models.Model):
    """
    Модель базы данных для приложения к счёту
    """
    # Устанавливается связь с таблицей InvoiceDNRDetails 1:1
    invoice = models.ForeignKey(
        InvoiceDNRDetails,
        related_name='invoice_details',
        on_delete=models.CASCADE  # Удаление деталей счёта удалит приложение
    )
    # Поле кода вида и условий оказания медицинской помощи.
    conditions_of_medical_care = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Вид и условие оказания медицинской помощи"
    )
    # Поле Фамилии, Имени и Отчества пациента
    patients_name = models.CharField(
        max_length=120,  # Максимум 120 символов
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Фамилия, Имя и Отчество пациента"
    )
    # Поле даты рождения пациента
    birthday = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата отчётного периода"  # Название поля
    )
    # Поле номера полиса медицинского страхования (ЕНП)
    policy_number = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Номер полиса обязательного медицинского страхования "
                  "застрахованного лица",  # Всплывающий текст подсказки
        verbose_name="ЕНП"  # Название поля
    )
    # Поле кода профиля медицинской помощи
    medical_care_profile_code = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Код профиля оказания медицинской помощи"  # Название поля
    )
    # Поле кода специальности врача
    doctors_specialty_code = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Кода специальности врача"  # Название поля
    )
    # Поле кода диагноза
    diagnosis = models.CharField(
        max_length=5,
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="МКБ-10",  # Всплывающий текст подсказки
        verbose_name="Кода диагноза"  # Название поля
    )
    # Поле даты начала лечения
    start_date_of_treatment = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата начала лечения"  # Название поля
    )
    # Поле даты окончания лечения
    end_date_of_treatment = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата окончания лечения"  # Название поля
    )
    # Поле кода результата лечения
    treatment_result_code = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Код результата лечения"  # Название поля
    )
    # Поле наименования результата лечения
    treatment_result_name = models.CharField(
        max_length=50,  # Максимум 5 символов
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Результат лечения"  # Название поля
    )
    # Поле объёма медицинской помощи
    volume_of_medical_care = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Объём медицинской помощи"  # Название поля
    )
    # Поле тарифа
    tariff = models.FloatField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Средний норматив финансовых затрат на единицу объема "
                  "медицинской помощи",  # Всплывающий текст подсказки
        verbose_name="Тариф"  # Название поля
    )
    # Поле совокупных расходов (tariff * volume_of_medical_care)
    expenses = models.FloatField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Расходы на оказание медицинской помощи",
        verbose_name="Тариф"  # Название поля
    )

# Список субъектов
class RegisterTerritorial(models.Model):
    """
    Модель таблицы для субъектов
    """
    code = models.IntegerField(
        blank=False,
        null=False,
        verbose_name="Код субъекта",
        unique=True
    )
    name = models.CharField(
        max_length=127,
        verbose_name="Название субъекта"
    )

    def __str__(self):
        return f"{self.code}: {self.name}"

# Список файлов счетов
class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result_file = models.FileField(upload_to='results/', null=True, blank=True)
