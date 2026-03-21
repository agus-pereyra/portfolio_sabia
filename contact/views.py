from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from phonenumber_field.phonenumber import to_python

def contact_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_raw = request.POST.get('phone', 'No provisto')
        message = request.POST.get('message')

        phone_formatted = None
        if phone_raw:
            phone_obj = to_python(phone_raw)
            if phone_obj and not phone_obj.is_valid():
                return JsonResponse({
                    'status': 'error', 
                    'message': 'El número de teléfono no es válido. Incluí el código de país (ej: +54).'
                }, status=400)
            phone_formatted = phone_obj

        try:
            # 1. Guardar en BD
            ContactMessage.objects.create(
                first_name=first_name, 
                last_name=last_name,
                email=email, 
                phone=phone_formatted, 
                message=message
            )

            # 2. Enviar Mail
            subject = f"Nueva propuesta: {first_name} {last_name}"
            body = f"""
            Nombre: {first_name} {last_name}
            Email: {email}
            Tel: {phone_raw}
            Mensaje:
            {message}
            """
            
            send_mail(
                subject, body, settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_RECIPIENT_EMAIL], fail_silently=False
            )

            return JsonResponse({'status': 'success', 'message': '¡Mensaje enviado!'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error en el servidor.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)