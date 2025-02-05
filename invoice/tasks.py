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