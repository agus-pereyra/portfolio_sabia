from django.forms.widgets import ClearableFileInput
from django.core.validators import FileExtensionValidator
from django import forms

class MultipleFileInput(ClearableFileInput):
    """Widget que permite seleccionar varios archivos a la vez."""
    allow_multiple_selected = True
 
class MultipleFileField(forms.FileField):
    """
    Campo genérico para subir múltiples archivos con validación de extensión.
    allowed_extensions=None para no restringir tipos.
    """
 
    def __init__(self, *args, allowed_extensions=None, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        if allowed_extensions:
            kwargs.setdefault('validators', [
                FileExtensionValidator(allowed_extensions=allowed_extensions)
            ])
        super().__init__(*args, **kwargs)
 
    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)
 
class MultipleMediaField(MultipleFileField):
    """Campo que acepta imágenes y videos en el mismo input."""
    IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp']
    VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi', 'webm']
 
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'allowed_extensions',
            self.IMAGE_EXTENSIONS + self.VIDEO_EXTENSIONS,
        )
        super().__init__(*args, **kwargs)
 
    def is_image(self, file):
        ext = file.name.rsplit('.', 1)[-1].lower()
        return ext in self.IMAGE_EXTENSIONS
 
    def is_video(self, file):
        ext = file.name.rsplit('.', 1)[-1].lower()
        return ext in self.VIDEO_EXTENSIONS
 
 
# Aliases de compatibilidad
class MultipleImageField(MultipleFileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['png', 'jpg', 'jpeg', 'webp'])
        super().__init__(*args, **kwargs)
 
 
class MultipleVideoField(MultipleFileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['mp4', 'mov', 'avi', 'webm'])
        super().__init__(*args, **kwargs)