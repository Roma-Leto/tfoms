# region Imports
import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponse

from .models import InvoiceDNRDetails, InvoiceAttachment, FileUpload, InvoiceInvoiceJobs
from .tasks import celery_save_second_sheet

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
        context['file'] = FileUpload.objects.get(parent_id=self.kwargs['pk'])
        # context['items'] = super().get_queryset().prefetch_related('invoice_att')
        # context["now"] = timezone.now()
        return context


def download_file(request, file_id, file_type):
    uploaded_file = get_object_or_404(FileUpload, id=file_id)

    if file_type == "original":
        file_path = uploaded_file.file.path
    elif file_type == "processed":
        file_path = uploaded_file.result_file.path
    else: # TODO: обработка ошибки
        return render(request, "app1/home.html", {"error": "Неверный тип файла!"})

    return FileResponse(open(default_storage.path(file_path), "rb"), as_attachment=True)


# ----------------------VVVV тест вызова процедуры VVVV-------------------------

from invoice.tasks import create_report


def excel_mock(request):
    """# удалить после отладки формирования отчёта"""
    create_report(39)
    return HttpResponse("200")
