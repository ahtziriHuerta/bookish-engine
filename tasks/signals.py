from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Producto
from django.conf import settings

@receiver(post_save, sender=Producto)
def verificar_stock_bajo(sender, instance, **kwargs):
    if instance.stock <= 3 and not instance.alerta_stock_enviada:
        send_mail(
            subject='⚠️ Alerta: Bajo Stock',
            message=f'El producto \"{instance.nombre}\" tiene solo {instance.stock} unidades disponibles.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['tiendacorozo@gmail.com'],
            fail_silently=False,
        )
        instance.alerta_stock_enviada = True
        instance.save(update_fields=['alerta_stock_enviada'])  # 👈 evita ciclo infinito de señales
