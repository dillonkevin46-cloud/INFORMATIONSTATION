from django.test import TestCase
from django.conf import settings
import os

class SettingsSecurityTests(TestCase):
    def test_debug_mode_is_false(self):
        """Ensure DEBUG is False by default for security."""
        # This test assumes the environment variable DEBUG is NOT set to 'True'
        # during the test run.
        if os.environ.get("DEBUG") == "True":
            return # Skip if explicitly enabled (e.g. for debugging tests)

        self.assertFalse(settings.DEBUG, "DEBUG should be False by default")

    def test_allowed_hosts_configured(self):
        """Ensure ALLOWED_HOSTS is not empty if DEBUG is False."""
        if not settings.DEBUG:
            self.assertTrue(len(settings.ALLOWED_HOSTS) > 0, "ALLOWED_HOSTS should not be empty when DEBUG is False")
