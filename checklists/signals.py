from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FormSubmission
from tickets.models import Ticket

@receiver(post_save, sender=FormSubmission)
def create_ticket_on_submission(sender, instance, created, **kwargs):
    if created and instance.template.form_type in ['onboarding', 'offboarding']:
        # Check if already linked to a ticket (unlikely if just created, but good practice)
        if instance.ticket:
            return

        title = f"{instance.template.get_form_type_display()}: {instance.submitted_by}"
        description = f"Automated ticket for {instance.template.title}.\nSubmitted by: {instance.submitted_by}\n"
        
        # Parse submission data if useful
        for key, value in instance.data.items():
            description += f"{key}: {value}\n"

        ticket = Ticket.objects.create(
            title=title,
            description=description,
            priority='medium',
            category=instance.template.form_type,
            client=instance.submitted_by if instance.submitted_by else None, # Assign to submitter
            # Assigned to? Maybe leave unassigned or assign to admin
        )
        
        # Link back
        instance.ticket = ticket
        instance.save()
