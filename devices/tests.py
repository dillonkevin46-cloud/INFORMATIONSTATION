from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Device

class DevicePaginationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.device_count = 15
        for i in range(self.device_count):
            Device.objects.create(
                hostname=f"device-{i}",
                local_ip=f"192.168.1.{i}",
                mac_address=f"00:00:00:00:00:{i:02x}"
            )

    def test_pagination_is_enabled(self):
        """
        Ensure that we get a paginated response.
        """
        response = self.client.get('/api/devices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check for pagination keys
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Check that we only get PAGE_SIZE results (10)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], self.device_count)

    def test_pagination_second_page(self):
        """
        Ensure that we can access the second page.
        """
        response = self.client.get('/api/devices/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that we get the remaining results (5)
        self.assertEqual(len(response.data['results']), 5)
