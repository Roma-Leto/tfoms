from openpyxl import load_workbook
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import UploadFileForm

def save_to_txt(data):
    with open("test.txt", "a") as file:
        for row in data:
            file.write(str(row))
    return 0

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

            # Загрузка Excel-файла с помощью openpyxl
            workbook = load_workbook(file, data_only=True)
            data_excel = list()
            # Итерируемся по всем листам
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]  # Получаем лист по имени
                print(f"Лист: {sheet_name}")  # Выводим имя листа

                # Итерируемся по строкам листа
                for row in sheet.iter_rows(values_only=True):
                    data_excel.append(row)
            save_to_txt(data_excel)  # Выводим данные строки

            # Сохранение данных в базу данных
            # for index, row in df.iter_rows():
            #     MyModel.objects.create(
            #         field1=row['column1'],
            #         field2=row['column2'],
            #         # и так далее...
            #     )

            # Перенаправление после успешной загрузки
            return HttpResponseRedirect('/upload_success/')
    else:
        form = UploadFileForm()
    return  render(request, 'invoice/upload.html', {'form': form})


# TODO: валидация данных
# TODO: обработка ошибок
# TODO: асинхронная обработка с помощью CELERY