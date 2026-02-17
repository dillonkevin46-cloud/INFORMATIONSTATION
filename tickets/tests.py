from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from devices.models import Device
from .models import Ticket

User = get_user_model()

class TicketModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='testclient',
            password='password123',
            role='client',
            email='client@example.com'
        )
        self.technician_user = User.objects.create_user(
            username='testtech',
            password='password123',
            role='technician',
            email='tech@example.com'
        )
        self.device = Device.objects.create(
            hostname='test-device',
            assigned_client=self.client_user
        )

    def test_create_ticket_minimal(self):
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='This is a test ticket.',
            client=self.client_user
        )
        self.assertIsNotNone(ticket.pk)
        self.assertEqual(ticket.title, 'Test Ticket')
        self.assertEqual(ticket.description, 'This is a test ticket.')
        self.assertEqual(ticket.client, self.client_user)
        self.assertEqual(ticket.status, 'new')
        self.assertEqual(ticket.priority, 'medium')

    def test_create_ticket_full(self):
        ticket = Ticket.objects.create(
            title='Full Ticket',
            description='Ticket with all fields',
            client=self.client_user,
            assigned_to=self.technician_user,
            device=self.device,
            priority='high',
            category='Hardware'
        )
        self.assertEqual(ticket.assigned_to, self.technician_user)
        self.assertEqual(ticket.device, self.device)
        self.assertEqual(ticket.priority, 'high')
        self.assertEqual(ticket.category, 'Hardware')

    def test_string_representation(self):
        ticket = Ticket.objects.create(
            title='String Test',
            description='Description',
            client=self.client_user
        )
        self.assertEqual(str(ticket), f"#{ticket.id} - String Test")

    def test_update_status_and_signal(self):
        ticket = Ticket.objects.create(
            title='Signal Test',
            description='Testing email signal',
            client=self.client_user
        )

        # Clear outbox just in case
        mail.outbox = []

        ticket.status = 'closed'
        ticket.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ticket Closed", mail.outbox[0].subject)
        self.assertIn(ticket.title, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.client_user.email])
