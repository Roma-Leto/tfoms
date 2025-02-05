# # tasks.py
# from io import BytesIO
#
# from celery import shared_task
# import openpyxl
# from .models import *
#
# @shared_task(bind=True)
# def process_file(self, file_data):
#     wb = openpyxl.load_workbook(filename=BytesIO(file_data))
#     ws = wb.active
#     total_rows = len(list(ws.rows))
#     # for index, row in enumerate(ws.iter_rows(values_only=True)):
#     #     InvoiceAttachment.objects.create(
#     #         column1=row[0],
#     #         column2=row[1],
#     #         ...
#     #         column15=row[14]
#     #     )
#     #     self.update_state(state='PROGRESS', meta={'current': index + 1, 'total': total_rows})
#     return 'Task completed successfully!'

# задача для обработки Excel-файла.
from celery import shared_task
import time
import pandas as pd
from .models import YourModel


@shared_task(bind=True)
def process_excel_file(self, file_path):
    # Открытие Excel файла
    df = pd.read_excel(file_path)

    total_rows = len(df)
    for index, row in df.iterrows():
        # Ваш код для записи данных в БД
        YourModel.objects.create(column1=row['column1'], column2=row['column2'])

        # Расчёт прогресса
        progress = int((index + 1) / total_rows * 100)
        self.update_state(state='PROGRESS',
                          meta={'current': index + 1, 'total': total_rows,
                                'progress': progress})

        time.sleep(0.1)  # Имитация долгой обработки
    return {'status': 'Task completed'}