import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User
from devices.models import Device, TelemetryData
from tickets.models import Ticket, TicketMessage
from knowledge_base.models import Article
from checklists.models import FormTemplate

class Command(BaseCommand):
    help = 'Seeds the database with initial data for demo purposes.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # 1. Create Users
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'role': 'admin'})
        if created:
            admin_user.set_password('admin')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        tech_user, created = User.objects.get_or_create(username='tech', defaults={'email': 'tech@example.com', 'role': 'technician'})
        if created:
            tech_user.set_password('tech')
            tech_user.save()

        client_user, created = User.objects.get_or_create(username='client', defaults={'email': 'client@example.com', 'role': 'client', 'company_name': 'Acme Corp'})
        if created:
            client_user.set_password('client')
            client_user.save()

        # 2. Create Devices
        devices_data = [
            {'hostname': 'DESKTOP-Main', 'local_ip': '192.168.1.10', 'os': 'Windows 10 Pro', 'online': True},
            {'hostname': 'SRV-FileShare', 'local_ip': '192.168.1.5', 'os': 'Windows Server 2019', 'online': True},
            {'hostname': 'LAPTOP-Sales01', 'local_ip': '192.168.1.101', 'os': 'Windows 11 Home', 'online': False},
            {'hostname': 'PRINTER-Reception', 'local_ip': '192.168.1.200', 'os': 'Firmware v2.1', 'online': True},
            {'hostname': 'WORKSTATION-Dev', 'local_ip': '192.168.1.15', 'os': 'Ubuntu 22.04', 'online': True},
        ]

        for d in devices_data:
            device, created = Device.objects.get_or_create(
                hostname=d['hostname'],
                defaults={
                    'local_ip': d['local_ip'],
                    'os_info': d['os'],
                    'is_online': d['online'],
                    'assigned_client': client_user,
                    'last_seen': timezone.now() if d['online'] else timezone.now() - timedelta(hours=random.randint(1, 48))
                }
            )

            # Add telemetry
            if created:
                for i in range(5):
                    TelemetryData.objects.create(
                        device=device,
                        cpu_usage=random.uniform(5, 90),
                        ram_usage=random.uniform(20, 80),
                        disk_usage=random.uniform(10, 60),
                        timestamp=timezone.now() - timedelta(minutes=i*10)
                    )
        self.stdout.write(self.style.SUCCESS(f'Created {len(devices_data)} devices'))

        # 3. Create Tickets
        tickets_data = [
            {'title': 'Printer not responding', 'priority': 'medium', 'status': 'open'},
            {'title': 'Server slow performance', 'priority': 'high', 'status': 'in_progress'},
            {'title': 'New user setup', 'priority': 'low', 'status': 'resolved'},
        ]

        for t in tickets_data:
            ticket, created = Ticket.objects.get_or_create(
                title=t['title'],
                defaults={
                    'description': 'Description for ' + t['title'],
                    'priority': t['priority'],
                    'status': t['status'],
                    'client': client_user,
                    'assigned_to': tech_user if t['status'] != 'new' else None
                }
            )
            if created:
                TicketMessage.objects.create(ticket=ticket, author=client_user, content="Please look into this issue.")
                if t['status'] != 'new':
                    TicketMessage.objects.create(ticket=ticket, author=tech_user, content="I am checking it now.")

        self.stdout.write(self.style.SUCCESS(f'Created {len(tickets_data)} tickets'))

        # 4. KB Articles
        if not Article.objects.exists():
            Article.objects.create(
                title="How to reset password",
                category="User Guide",
                content="1. Go to settings.\n2. Click Security.\n3. Change Password.",
                author=admin_user,
                is_public=True
            )
            Article.objects.create(
                title="VPN Setup for Remote Access",
                category="Network",
                content="Instructions for setting up VPN client...",
                author=tech_user,
                is_public=False
            )
            self.stdout.write(self.style.SUCCESS('Created KB articles'))

        # 5. Checklists
        if not FormTemplate.objects.exists():
            FormTemplate.objects.create(
                title="New Employee Onboarding",
                description="Checklist for IT setup of new hires.",
                form_type='onboarding',
                fields=[
                    {'label': 'Employee Name', 'type': 'text', 'required': True},
                    {'label': 'Create Email Account', 'type': 'checkbox', 'required': True},
                    {'label': 'Assign Laptop', 'type': 'checkbox', 'required': True},
                    {'label': 'Notes', 'type': 'textarea', 'required': False},
                ]
            )
            self.stdout.write(self.style.SUCCESS('Created Checklist template'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
