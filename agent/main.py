import asyncio
import websockets
import json
import platform
import socket
import psutil
import uuid
import argparse
import os
import threading
import subprocess
import base64
import io
import time
from datetime import datetime

# GUI Libraries (wrapped for headless support)
try:
    import pystray
    from PIL import Image
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI libraries not found. Running in headless mode.")
except Exception as e:
    GUI_AVAILABLE = False
    print(f"GUI initialization failed: {e}. Running in headless mode.")

try:
    import mss
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

# Configuration
DEFAULT_SERVER_URL = "ws://localhost:8000/ws/agent/"
SERVER_URL = DEFAULT_SERVER_URL
AGENT_VERSION = "1.1.0"

# Global websocket reference for GUI actions
metrics_websocket = None

def get_mac_address():
    mac_num = uuid.getnode()
    mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
    return mac

def get_system_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        "public_ip": "127.0.0.1", # Placeholder
        "agent_version": AGENT_VERSION
    }

async def heartbeat_task(websocket):
    while True:
        try:
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
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(5)
        except websockets.exceptions.ConnectionClosed:
            print("Heartbeat: Connection closed")
            break
        except Exception as e:
            print(f"Heartbeat error: {e}")
            break

async def receive_task(websocket):
    global metrics_websocket
    metrics_websocket = websocket
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                content = data.get('content', {}) # Sometimes wrapped in content

                # Handle direct commands or wrapped commands
                if msg_type == 'command':
                    cmd = data.get('command') or content.get('command')
                    await handle_command(websocket, cmd)
                elif msg_type == 'get_screenshot':
                    await handle_screenshot(websocket)
                elif msg_type == 'handshake_ack':
                    print(f"Registered with ID: {data.get('device_id')}")
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Error processing message: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("Receive: Connection closed")

async def handle_command(websocket, cmd):
    if not cmd:
        return

    print(f"Executing command: {cmd}")
    try:
        # Run command
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = proc.stdout + proc.stderr

        response = {
            "type": "command_response",
            "data": {
                "command": cmd,
                "output": output,
                "exit_code": proc.returncode,
                "timestamp": datetime.now().isoformat()
            }
        }
        await websocket.send(json.dumps(response))
    except subprocess.TimeoutExpired:
        await websocket.send(json.dumps({
            "type": "command_response",
            "data": {"command": cmd, "output": "Timeout expired", "exit_code": -1}
        }))
    except Exception as e:
        await websocket.send(json.dumps({
            "type": "command_response",
            "data": {"command": cmd, "output": str(e), "exit_code": -1}
        }))

async def handle_screenshot(websocket):
    if not SCREENSHOT_AVAILABLE:
        await websocket.send(json.dumps({
            "type": "screenshot_response",
            "error": "Screenshot library not available"
        }))
        return

    try:
        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            # Compress to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=50)
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

            response = {
                "type": "screenshot",
                "data": {
                    "image": img_str,
                    "timestamp": datetime.now().isoformat()
                }
            }
            await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Screenshot error: {e}")
        await websocket.send(json.dumps({
            "type": "screenshot_response",
            "error": str(e)
        }))

async def agent_loop():
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
            print("Connection refused. Retrying in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

def run_async_loop():
    asyncio.run(agent_loop())

# GUI Callbacks
def on_report_issue(icon, item):
    if not GUI_AVAILABLE:
        print("Report Issue triggered (Headless mode)")
        return

    try:
        root = tk.Tk()
        root.withdraw() # Hide main window
        issue_text = simpledialog.askstring("Report Issue", "Describe the issue:")
        if issue_text:
            # In a real app, send this to server via websocket
            # For now, just print or simulate
            print(f"Issue Reported: {issue_text}")
            messagebox.showinfo("Success", "Issue reported successfully.")
        root.destroy()
    except Exception as e:
        print(f"GUI Error: {e}")

def on_network_test(icon, item):
    print("Running Network Test...")
    try:
        # Simple ping test
        param = '-n' if platform.system().lower()=='windows' else '-c'
        cmd = ['ping', param, '1', '8.8.8.8']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            msg = "Network is reachable."
        else:
            msg = "Network is unreachable."

        if GUI_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("Network Test", msg)
            root.destroy()
        print(msg)
    except Exception as e:
        print(f"Network Test Error: {e}")

def create_tray_icon():
    if not GUI_AVAILABLE:
        return None

    try:
        # Create a simple icon (color block) if no image file
        image = Image.new('RGB', (64, 64), color=(0, 212, 255))

        menu = pystray.Menu(
            pystray.MenuItem("Report Issue", on_report_issue),
            pystray.MenuItem("Network Test", on_network_test),
            pystray.MenuItem("Exit", lambda icon, item: icon.stop())
        )

        icon = pystray.Icon("Omni-RMM", image, "Omni-RMM Agent", menu)
        return icon
    except Exception as e:
        print(f"Failed to create tray icon: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omni-RMM Agent")
    parser.add_argument("--server", type=str, help="WebSocket URL")
    args = parser.parse_args()
    
    if args.server:
        SERVER_URL = args.server
    elif os.environ.get("RMM_SERVER_URL"):
        SERVER_URL = os.environ.get("RMM_SERVER_URL")

    # Start asyncio loop in a separate thread
    t = threading.Thread(target=run_async_loop, daemon=True)
    t.start()

    # Run GUI in main thread if available
    if GUI_AVAILABLE:
        try:
            icon = create_tray_icon()
            if icon:
                icon.run()
            else:
                # If icon creation failed (e.g. no display), just join thread
                print("Running in headless mode (Icon creation failed).")
                t.join()
        except Exception as e:
            print(f"GUI Crash: {e}. Running headless.")
            t.join()
    else:
        print("Running in headless mode.")
        t.join()
