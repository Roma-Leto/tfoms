from django import forms


class UploadFileForm(forms.Form):
    """
    Класс загрузки файла в формате excel
    """
    file = forms.FileField()
