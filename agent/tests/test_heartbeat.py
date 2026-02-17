import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

# Mock dependencies before import
sys.modules['psutil'] = MagicMock()
# We need to mock websockets and its exceptions
mock_websockets = MagicMock()
class MockConnectionClosed(Exception):
    pass
mock_websockets.exceptions.ConnectionClosed = MockConnectionClosed
sys.modules['websockets'] = mock_websockets

sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['mss'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now import agent.main
from agent import main

import asyncio
import json

class TestHeartbeat(unittest.IsolatedAsyncioTestCase):
    async def test_heartbeat_metric_failure(self):
        """Test that metric collection failures do not stop the heartbeat."""
        mock_ws = AsyncMock()

        # Configure psutil mocks to raise exceptions
        main.psutil.cpu_percent.side_effect = Exception("CPU Error")
        main.psutil.virtual_memory.side_effect = Exception("RAM Error")
        main.psutil.disk_usage.side_effect = Exception("Disk Error")

        # We want to run the loop once. We can patch asyncio.sleep to raise a custom exception to break the loop
        class StopLoop(Exception): pass

        with patch('asyncio.sleep', side_effect=StopLoop):
            try:
                await main.heartbeat_task(mock_ws)
            except StopLoop:
                pass

        # Verify send was called
        self.assertTrue(mock_ws.send.called)
        call_args = mock_ws.send.call_args[0][0]
        data = json.loads(call_args)

        self.assertEqual(data['type'], 'heartbeat')
        # Expect 0 values due to error handling we are about to implement
        # (Current code will crash, so this test is expected to fail on current code if we didn't handle exceptions properly)
        # Actually current code:
        # psutil.cpu_percent raises Exception -> caught by outer 'except Exception' -> breaks loop.
        # So send is NEVER called if cpu_percent fails.
        # So this test confirms the fix.

        # If we run this on CURRENT code:
        # psutil.cpu_percent raises.
        # Caught by except Exception.
        # Loop breaks.
        # mock_ws.send is NOT called.
        # Test fails.

        self.assertEqual(data['data']['cpu_usage'], 0)
        self.assertEqual(data['data']['ram_usage'], 0)
        self.assertEqual(data['data']['disk_usage'], 0)

    async def test_heartbeat_connection_closed(self):
        """Test that ConnectionClosed exception breaks the loop cleanly."""
        mock_ws = AsyncMock()
        mock_ws.send.side_effect = main.websockets.exceptions.ConnectionClosed()

        # Should just return without raising
        await main.heartbeat_task(mock_ws)

    async def test_heartbeat_unexpected_error(self):
        """Test that unexpected errors break the loop."""
        mock_ws = AsyncMock()
        mock_ws.send.side_effect = Exception("Unexpected")

        # Should just return (after printing error)
        await main.heartbeat_task(mock_ws)

if __name__ == '__main__':
    unittest.main()
