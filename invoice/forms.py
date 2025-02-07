from django import forms

from .models import InvoiceDNRDetails

class UploadFileForm(forms.Form):
    """
    Класс загрузки файла в формате excel
    """
    file = forms.FileField()


class DNRDetailsForm(forms.Form):
    class Meta:
        model = InvoiceDNRDetails
        fields = ['invoice_number',
                  'code_fund',
                  'mouth_of_invoice_receipt',
                  'year_of_invoice_receipt',
                  'date_of_reporting_period',
                  'total_amount'
                  ]

