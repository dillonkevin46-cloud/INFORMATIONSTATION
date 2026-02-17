from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'role': 'client',
            'phone': '1234567890',
            'company_name': 'Test Company'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test user creation with all fields."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertEqual(self.user.role, 'client')
        self.assertEqual(self.user.phone, '1234567890')
        self.assertEqual(self.user.company_name, 'Test Company')

    def test_user_default_role(self):
        """Test that the default role is 'client'."""
        user = get_user_model().objects.create_user(username='defaultroleuser', password='password')
        self.assertEqual(user.role, 'client')

    def test_user_str(self):
        """Test the string representation of the user."""
        self.assertEqual(str(self.user), 'testuser (client)')

    def test_user_roles(self):
        """Test creating users with different roles."""
        admin_user = get_user_model().objects.create_user(username='admin', password='password', role='admin')
        self.assertEqual(admin_user.role, 'admin')
        self.assertEqual(str(admin_user), 'admin (admin)')

        technician_user = get_user_model().objects.create_user(username='technician', password='password', role='technician')
        self.assertEqual(technician_user.role, 'technician')
        self.assertEqual(str(technician_user), 'technician (technician)')

    def test_optional_fields(self):
        """Test that phone and company_name can be null/blank."""
        user = get_user_model().objects.create_user(username='minimaluser', password='password')
        self.assertIsNone(user.phone)
        self.assertIsNone(user.company_name)
