from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Device, TelemetryData
import json
import logging
import traceback

logger = logging.getLogger(__name__)

class AgentConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.device_id = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.device_id:
            await self.update_device_status(online=False)
            await self.channel_layer.group_discard(
                f"device_{self.device_id}",
                self.channel_name
            )

    async def receive_json(self, content):
        try:
            message_type = content.get('type')
            data = content.get('data')

            if message_type == 'handshake':
                await self.handle_handshake(data)
            elif message_type == 'heartbeat':
                await self.handle_heartbeat(data)
            elif message_type == 'command_response':
                await self.broadcast_to_browser('command_response', data)
            elif message_type == 'screenshot':
                await self.broadcast_to_browser('screenshot', data)
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()

    async def broadcast_to_browser(self, msg_type, data):
        if self.device_id:
            await self.channel_layer.group_send(
                f"device_{self.device_id}_browser",
                {
                    "type": "browser.message",
                    "message": {
                        "type": msg_type,
                        "data": data
                    }
                }
            )

    async def handle_handshake(self, data):
        try:
            device = await self.get_or_create_device(data)
            if not device:
                logger.error("Failed to authenticate device: get_or_create_device returned None")
                await self.close()
                return

            self.device_id = str(device.id)
            
            # Agent listens on this group for commands from server
            await self.channel_layer.group_add(
                f"device_{self.device_id}",
                self.channel_name
            )
            
            await self.send_json({
                'type': 'handshake_ack',
                'status': 'success',
                'device_id': self.device_id
            })
            print(f"Device connected: {self.device_id}")
        except Exception as e:
            print(f"Handshake error: {e}")
            traceback.print_exc()
            await self.close()

    async def handle_heartbeat(self, data):
        if not self.device_id:
            return
        try:
            await self.save_telemetry(data)
            await self.update_last_seen()
            # Optional: Broadcast heartbeat to browser for live status?
            await self.broadcast_to_browser('heartbeat', data)
        except Exception as e:
            print(f"Heartbeat error: {e}")

    @database_sync_to_async
    def get_or_create_device(self, data):
        mac = data.get('mac_address')
        if not mac:
            raise ValueError("MAC address required")
            
        defaults = {
            'hostname': data.get('hostname'),
            'os_info': data.get('os_info'),
            'local_ip': data.get('local_ip'),
            'public_ip': data.get('public_ip'),
            'agent_version': data.get('agent_version'),
            'last_seen': timezone.now(),
            'is_online': True
        }
        
        device, created = Device.objects.update_or_create(
            mac_address=mac,
            defaults=defaults
        )
        return device

    @database_sync_to_async
    def update_device_status(self, online):
        if self.device_id:
            Device.objects.filter(id=self.device_id).update(is_online=online, last_seen=timezone.now())

    @database_sync_to_async
    def update_last_seen(self):
        if self.device_id:
             Device.objects.filter(id=self.device_id).update(last_seen=timezone.now(), is_online=True)

    @database_sync_to_async
    def save_telemetry(self, data):
        if self.device_id:
            TelemetryData.objects.create(
                device_id=self.device_id,
                cpu_usage=data.get('cpu_usage', 0),
                ram_usage=data.get('ram_usage', 0),
                disk_usage=data.get('disk_usage', 0)
            )
            
    async def device_command(self, event):
        """
        Handler for commands sent from server to agent
        """
        await self.send_json(event['content'])


class DeviceBrowserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        await self.channel_layer.group_add(
            f"device_{self.device_id}_browser",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"device_{self.device_id}_browser",
            self.channel_name
        )

    async def receive_json(self, content):
        # Handle commands from browser to agent (e.g., "get_screenshot")
        message_type = content.get('type')
        if message_type == 'command':
            # Forward command to Agent group
            await self.channel_layer.group_send(
                f"device_{self.device_id}",
                {
                    "type": "device.command",
                    "content": {
                        "type": "command",
                        "command": content.get('command')
                    }
                }
            )
        elif message_type == 'get_screenshot':
            await self.channel_layer.group_send(
                f"device_{self.device_id}",
                {
                    "type": "device.command",
                    "content": {
                        "type": "get_screenshot"
                    }
                }
            )

    async def browser_message(self, event):
        """
        Receive message from AgentConsumer and send to Browser
        """
        await self.send_json(event['message'])
