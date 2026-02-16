from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Device, TelemetryData
import json

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
        message_type = content.get('type')
        data = content.get('data')

        if message_type == 'handshake':
            await self.handle_handshake(data)
        elif message_type == 'heartbeat':
            await self.handle_heartbeat(data)
        elif message_type == 'command_response':
            # Handle command response from agent
            pass

    async def handle_handshake(self, data):
        """
        Register or update the device based on MAC address.
        """
        # data: {hostname, mac_address, os_info, local_ip, public_ip, agent_version}
        device = await self.get_or_create_device(data)
        self.device_id = str(device.id)

        # Add to device specific group for targeted commands
        await self.channel_layer.group_add(
            f"device_{self.device_id}",
            self.channel_name
        )

        await self.send_json({
            'type': 'handshake_ack',
            'status': 'success',
            'device_id': self.device_id
        })

    async def handle_heartbeat(self, data):
        if not self.device_id:
            return

        # Update last seen and telemetry
        await self.save_telemetry(data)
        await self.update_last_seen()

    @database_sync_to_async
    def get_or_create_device(self, data):
        mac = data.get('mac_address')
        if not mac:
            # Fallback or error handling
            return None

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
        Handler for messages sent from the server (admin) to this consumer via channel layer.
        event: {'type': 'device_command', 'content': {'command': 'reboot', ...}}
        """
        await self.send_json(event['content'])
