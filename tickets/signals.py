from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Ticket

@receiver(pre_save, sender=Ticket)
def notify_on_close(sender, instance, **kwargs):
    if instance.id:
        old_ticket = Ticket.objects.get(id=instance.id)
        if old_ticket.status != 'closed' and instance.status == 'closed':
            # Status changed to closed
            if instance.client and instance.client.email:
                send_mail(
                    f"Ticket Closed: #{instance.id} - {instance.title}",
                    f"Your ticket has been marked as closed.\n\nDescription: {instance.description}\n\nResolution: (Check ticket details)",
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.client.email],
                    fail_silently=False,
                )
