from django.forms.widgets import ClearableFileInput
from django.core.validators import FileExtensionValidator
from django import forms

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())

        kwargs.setdefault("validators", [
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp'])
        ])
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultipleVideoField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        
        kwargs.setdefault("validators", [
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'webm'])
        ])
        
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # Limpiamos y validamos cada video de la lista
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result