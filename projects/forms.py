import pathlib
from django import forms
from django.core.exceptions import ValidationError


def check_file(file):
    # Допустимые форматы файла
    check_format = ['.json']

    # Если файл больше 5мб - 5242880 байт
    if file.size > 5242880:
        raise ValidationError('Файл больше 5 мегабайт')
    if pathlib.Path(file.name).suffix not in check_format:
        raise ValidationError('Недопустимый формат файла')
    return True


class UploadJsonFileForm(forms.Form):
    json_file = forms.FileField(label="Выберите JSON файл")

    def clean(self):
        if check_file(self.cleaned_data['json_file']):
            return self.cleaned_data





