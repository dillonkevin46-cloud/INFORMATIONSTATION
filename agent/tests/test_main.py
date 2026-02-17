import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import logging
import sys
import os

# Mock missing dependencies
sys.modules['websockets'] = MagicMock()
sys.modules['websockets.exceptions'] = MagicMock()
sys.modules['websockets.exceptions'].ConnectionClosed = Exception # Mock exception class
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['mss'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Add parent directory (agent) to path so we can import main
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(agent_dir)

try:
    import main
except ImportError as e:
    print(f"Failed to import main: {e}")
    sys.exit(1)

class TestAgentLogging(unittest.IsolatedAsyncioTestCase):
    async def test_json_decode_error_logging(self):
        # Create a mock websocket that yields one invalid JSON message then stops

        class MockWebsocket:
            def __init__(self, messages):
                self.messages = messages
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index < len(self.messages):
                    msg = self.messages[self.index]
                    self.index += 1
                    return msg
                else:
                    raise StopAsyncIteration

        mock_ws = MockWebsocket(['invalid-json'])

        # Capture logs
        # This will fail if no logs are emitted (which is expected initially)
        with self.assertLogs(level='ERROR') as cm:
            await main.receive_task(mock_ws)

        # Verify that an error was logged
        self.assertTrue(any("JSON" in log for log in cm.output))

if __name__ == '__main__':
    unittest.main()
