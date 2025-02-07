from django import forms

from .models import InvoiceDNRDetails

class UploadFileForm(forms.Form):
    """
    Класс загрузки файла в формате excel
    """
    file = forms.FileField()


class DNRDetailsForm(forms.Form):
    invoice_number = forms.IntegerField()

    class Meta:
        model = InvoiceDNRDetails
        fields = ['mouth_of_invoice_receipt',
                  'year_of_invoice_receipt',
                  'date_of_reporting_period',
                  'code_fund',
                  'invoice_number',
                  'total_amount'
                  ]
