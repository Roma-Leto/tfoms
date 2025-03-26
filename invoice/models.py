"""
Описание моделей базы данных для приложения обработки счетов Invoice
"""
import os

from django.db import models
from django.db.models import UniqueConstraint
import uuid


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
        verbose_name="Месяц отчётного периода"  # Название поля
    )
    # Поле даты поступления счёта
    year_of_invoice_receipt = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Год отчётного периода"  # Название поля
    )
    # Поле даты отчётного периода
    date_of_reporting_period = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата поступления счёта"  # Название поля
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
    ext_id = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    # file_origin = models.FileField(upload_to='results/')
    # file_result = models.FileField(upload_to='results/')

    class Meta:
        pass

    def __str__(self):
        return str(self.invoice_number)

# Записи пациентов
class InvoiceAttachment(models.Model):
    """
    Модель базы данных для приложения к счёту
    """
    # Устанавливается связь с таблицей InvoiceDNRDetails 1:1
    ext = models.ForeignKey(
        InvoiceDNRDetails,
        related_name='invoice_att',
        # to_field='ext_id',
        # db_column='ext_id',
        # primary_key=True,
        # related_query_name='invoice_att',
        on_delete=models.CASCADE  # Удаление деталей счёта удалит приложение
    )
    usl_ok = models.IntegerField(
        # Производная от row_id
        null=True,
        verbose_name="Условия оказания медицинской помощи"
    )
    row_id = models.CharField(
        max_length=10,
        verbose_name="Условия оказания медицинской помощи"
    )
    # Поле Фамилии, Имени и Отчества пациента
    fio = models.CharField(
        max_length=255,  # Максимум 120 символов
        null=True,  # Поле может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Фамилия, Имя и Отчество пациента"
    )
    mocod = models.IntegerField(
        null=True,
        verbose_name="№ п/п"  # Название поля
    )
    tip = models.CharField(
        max_length=50,
        verbose_name="Единица измерения"  # Название поля
    )
    dr = models.DateField(
        null=True,
        verbose_name="Дата рождения пациента"  # Название поля
    )
    # Поле номера полиса медицинского страхования (ЕНП)
    enp = models.PositiveBigIntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Номер полиса обязательного медицинского страхования "
                  "застрахованного лица",  # Всплывающий текст подсказки
        verbose_name="ЕНП"  # Название поля
    )
    subj_n = models.CharField(
        max_length=255,
        help_text="Наименование субъекта где выдан полис",  # Всплывающий текст подсказки
        verbose_name="Субъект где выдан полис"  # Название поля
    )
    # Поле кода профиля медицинской помощи
    profil_id = models.IntegerField(
        verbose_name="Код профиля оказания медицинской помощи"  # Название поля
    )
    profil_n = models.CharField(
        max_length=255,
        verbose_name="Наименование профиля оказания медицинской помощи"  # Название поля
    )
    # Поле кода специальности врача
    spec_id = models.IntegerField(
        verbose_name="Кода специальности врача"  # Название поля
    )
    spec_n = models.CharField(
        max_length=255,
        verbose_name="Наименование специальности врача"  # Название поля
    )
    # Поле кода диагноза
    dz = models.CharField(
        max_length=20,
        null=True,
        blank=False,  # Поле не может быть пустым
        help_text="МКБ-10",  # Всплывающий текст подсказки
        verbose_name="Кода диагноза"  # Название поля
    )
    # Поле даты начала лечения
    date1 = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата начала лечения"  # Название поля
    )
    # Поле даты окончания лечения
    date2 = models.DateField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Дата окончания лечения"  # Название поля
    )
    # Поле кода результата лечения
    rslt_id = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Код результата лечения"  # Название поля
    )
    # Поле наименования результата лечения
    rslt_n = models.CharField(
        max_length=127,  # Максимум 127 символов
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Результат лечения"  # Название поля
    )
    # Поле объёма медицинской помощи
    cnt_usl = models.IntegerField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        verbose_name="Объём медицинской помощи"  # Название поля
    )
    # Поле тарифа
    tarif = models.FloatField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Средний норматив финансовых затрат на единицу объема "
                  "медицинской помощи",  # Всплывающий текст подсказки
        verbose_name="Тариф"  # Название поля
    )
    # Поле совокупных расходов (tariff * volume_of_medical_care)
    sum_usl = models.FloatField(
        null=False,  # Поле не может быть NULL
        blank=False,  # Поле не может быть пустым
        help_text="Расходы на оказание медицинской помощи",
        verbose_name="Тариф"  # Название поля
    )
    
    id_pac = models.IntegerField(null=True)  # Признак завершения идентификации
    pid = models.IntegerField(null=True)  # Идентификатор застрахованного лица
    smo_id = models.CharField(max_length=30, null=True)  # Страховая медицинская организация
    enp_id = models.CharField(max_length=16, null=True)  # ЕНП после идентификации
    w_id = models.IntegerField(null=True)  # пол персоны из ФЕРЗЛ
    oip_id = models.CharField(max_length=12, null=True)  # уникальный идентификатор персоны в ФЕРЗЛ
    okato_id = models.CharField(max_length=10, null=True)  # ОКАТО территории страхования в ФЕРЗЛ
    req_id = models.IntegerField(null=True)  # код запроса
    req_result = models.CharField(max_length=255, null=True)  # результат идентификации в ФЕРЗЛ




    class Meta:
        unique_together = ('enp', 'dr', 'date1', 'date2')
        constraints = [
            UniqueConstraint(fields=['enp', 'dr', 'date1', 'date2'],
                             name='unique_combination')
        ]

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
    parent = models.OneToOneField(InvoiceDNRDetails, on_delete=models.CASCADE)

    def __str__(self):
        return os.path.basename(self.file.name)

# View из MS SQL
class InvoiceErrors(models.Model):
    ext_id = models.BigIntegerField(blank=True, null=True)
    attachment_id = models.BigIntegerField(blank=True, null=True)
    error_list = models.CharField(max_length=8000)
    error_text = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False  # Нельзя управлять таблицей
        unique_together = ('ext_id', 'attachment_id')
        db_table = 'invoice_errors'

    # Переопределяем менеджер, чтобы отключить проверку первичного ключа
    objects = models.Manager()

class InvoiceInvoiceJobs(models.Model):
    """Таблица флагов для отслеживания этапов обработки данных"""
    id = models.BigAutoField(primary_key=True)
    ext = models.ForeignKey('InvoiceDNRDetails', models.DO_NOTHING)
    step = models.ForeignKey('InvoiceInvoicejobSteps', models.DO_NOTHING)
    # status = models.CharField(max_length=255, db_collation='Cyrillic_General_CI_AS')
    status = models.CharField(max_length=2048)
    ready = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'invoice_invoicejobs'


class InvoiceInvoiceJobSteps(models.Model):
    """Таблица с названиями этапов  обработки данных"""
    id = models.BigAutoField(primary_key=True)
    # step_name = models.CharField(max_length=36, db_collation='Cyrillic_General_CI_AS')
    step_name = models.CharField(max_length=36)
    step_order = models.IntegerField(unique=True)

    class Meta:
        managed = True
        db_table = 'invoice_invoicejob_steps'
