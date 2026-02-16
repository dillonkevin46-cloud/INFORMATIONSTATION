import asyncio
import websockets
import json
import platform
import socket
import psutil
import uuid
import argparse
import os

# Configuration
# Default URL
DEFAULT_SERVER_URL = "ws://localhost:8000/ws/agent/"
SERVER_URL = DEFAULT_SERVER_URL
AGENT_VERSION = "1.0.0"

def get_mac_address():
    mac_num = uuid.getnode()
    mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
    return mac

def get_system_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google DNS to determine local IP (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    return {
        "hostname": socket.gethostname(),
        "os_info": f"{platform.system()} {platform.release()}",
        "mac_address": get_mac_address(),
        "local_ip": local_ip,
        "public_ip": "127.0.0.1", # Placeholder, would query external service
        "agent_version": AGENT_VERSION
    }

async def heartbeat_task(websocket):
    while True:
        try:
            # Gather metrics
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            try:
                disk = psutil.disk_usage('/').percent
            except:
                disk = 0

            payload = {
                "type": "heartbeat",
                "data": {
                    "cpu_usage": cpu,
                    "ram_usage": ram,
                    "disk_usage": disk
                }
            }
            # print(f"Sending heartbeat: {payload}")
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(5)
        except websockets.exceptions.ConnectionClosed:
            print("Heartbeat: Connection closed")
            break
        except Exception as e:
            print(f"Heartbeat error: {e}")
            break

async def receive_task(websocket):
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            try:
                data = json.loads(message)
                # Process command
                if data.get('type') == 'handshake_ack':
                    print(f"Registered with ID: {data.get('device_id')}")
                elif data.get('type') == 'command':
                    # Execute command
                    pass
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        print("Receive: Connection closed")

async def agent_main():
    while True:
        try:
            print(f"Connecting to {SERVER_URL}...")
            async with websockets.connect(SERVER_URL) as websocket:
                print("Connected!")

                # Handshake
                info = get_system_info()
                await websocket.send(json.dumps({
                    "type": "handshake",
                    "data": info
                }))

                # Start tasks
                producer = asyncio.create_task(heartbeat_task(websocket))
                consumer = asyncio.create_task(receive_task(websocket))

                done, pending = await asyncio.wait(
                    [producer, consumer],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()

        except ConnectionRefusedError:
            print("Connection refused. Server might be down. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omni-RMM Agent")
    parser.add_argument("--server", type=str, help="WebSocket URL of the server")
    args = parser.parse_args()

    if args.server:
        SERVER_URL = args.server
    elif os.environ.get("RMM_SERVER_URL"):
        SERVER_URL = os.environ.get("RMM_SERVER_URL")

    try:
        asyncio.run(agent_main())
    except KeyboardInterrupt:
        print("Agent stopped.")
