from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    email = models.EmailField(verbose_name="Email")
    phone = PhoneNumberField(blank=True, null=True, verbose_name="Teléfono", help_text="(Opcional)")
    message = models.TextField(verbose_name="Mensaje/Propuesta")
    created_at = models.DateTimeField(auto_now_add=True)

    def __clase__(self):
        return f"Mensaje de {self.first_name} {self.last_name} ({self.email})"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.created_at.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-created_at']