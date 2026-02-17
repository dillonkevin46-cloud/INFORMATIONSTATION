from django.test import TestCase, Client
from django.urls import reverse
from devices.models import Device

class DashboardSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a sample device with sensitive info
        Device.objects.create(
            hostname="sensitive-host",
            local_ip="192.168.1.100",
            os_info="Ubuntu 22.04",
            is_online=True
        )

    def test_dashboard_requires_login(self):
        """
        Verify that the dashboard requires authentication.
        """
        response = self.client.get(reverse('dashboard'))
        # Should be 302 (redirect to login).
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_api_requires_login(self):
        """
        Verify that the device API requires authentication.
        """
        # The router registers 'devices' as 'device-list' by default
        response = self.client.get('/api/devices/')
        # Should be 403 Forbidden for unauthenticated access in DRF
        self.assertEqual(response.status_code, 403)

    def test_dashboard_info_disclosure_redirection(self):
        """
        Verify that sensitive info is NOT present in the response when not logged in.
        """
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertNotIn(b"sensitive-host", response.content)
        self.assertNotIn(b"192.168.1.100", response.content)
