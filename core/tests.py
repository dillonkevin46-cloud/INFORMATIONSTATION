from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')
        self.chart_data_url = reverse('dashboard_chart_data')
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_dashboard_access_unauthenticated(self):
        """
        Ensure unauthenticated users are redirected to the login page when accessing the dashboard.
        """
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.dashboard_url}')

    def test_chart_data_access_unauthenticated(self):
        """
        Ensure unauthenticated users are redirected to the login page when accessing chart data.
        """
        response = self.client.get(self.chart_data_url)
        # API endpoints protected by @login_required typically return 302 to login page unless handled by DRF permissions
        # Since these are standard views, they will redirect.
        self.assertRedirects(response, f'/accounts/login/?next={self.chart_data_url}')

    def test_dashboard_access_authenticated(self):
        """
        Ensure authenticated users can access the dashboard.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_chart_data_access_authenticated(self):
        """
        Ensure authenticated users can access chart data.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.chart_data_url)
        self.assertEqual(response.status_code, 200)
