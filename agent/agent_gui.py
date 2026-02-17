import tkinter as tk
from tkinter import messagebox, simpledialog
import asyncio
import threading
import json
import websockets
import platform
import socket
import psutil
import uuid
import os
import sys

# Configuration
DEFAULT_SERVER_URL = "ws://localhost:8000/ws/agent/"
SERVER_URL = os.environ.get("RMM_SERVER_URL", DEFAULT_SERVER_URL)
AGENT_VERSION = "1.0.0"

# --- WebSocket Logic (From main.py, adapted for GUI) ---

class AgentClient:
    def __init__(self, gui):
        self.gui = gui
        self.websocket = None
        self.device_id = None
        self.running = True
        self.loop = asyncio.new_event_loop()

    def get_mac_address(self):
        mac_num = uuid.getnode()
        mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
        return mac

    def get_system_info(self):
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
            "mac_address": self.get_mac_address(),
            "local_ip": local_ip,
            "public_ip": "127.0.0.1",
            "agent_version": AGENT_VERSION
        }

    async def heartbeat_task(self):
        while self.running:
            if self.websocket:
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
                    await self.websocket.send(json.dumps(payload))
                except Exception as e:
                    print(f"Heartbeat error: {e}")
                    self.websocket = None # Force reconnect
            await asyncio.sleep(5)

    async def receive_task(self):
        while self.running:
            if self.websocket:
                try:
                    async for message in self.websocket:
                        print(f"Received: {message}")
                        try:
                            data = json.loads(message)
                            if data.get('type') == 'handshake_ack':
                                self.device_id = data.get('device_id')
                                self.gui.update_status("Connected", "green")
                            elif data.get('type') == 'command_exec':
                                # Handle remote command
                                cmd = data.get('command')
                                output = os.popen(cmd).read()
                                await self.websocket.send(json.dumps({
                                    "type": "command_result",
                                    "data": output
                                }))
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    print(f"Receive error: {e}")
                    self.gui.update_status("Disconnected", "red")
                    self.websocket = None
            else:
                await asyncio.sleep(1)

    async def connect(self):
        while self.running:
            try:
                self.gui.update_status("Connecting...", "orange")
                async with websockets.connect(SERVER_URL) as ws:
                    self.websocket = ws

                    # Handshake
                    info = self.get_system_info()
                    await ws.send(json.dumps({
                        "type": "handshake",
                        "data": info
                    }))

                    # Run tasks
                    await asyncio.gather(
                        self.heartbeat_task(),
                        self.receive_task()
                    )
            except Exception as e:
                self.gui.update_status("Connection Failed", "red")
                print(f"Connection failed: {e}")
                self.websocket = None
                await asyncio.sleep(5)

    def start(self):
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    def send_ticket(self, title, description):
        # In a real app, this might go via HTTP API or WS
        # For simplicity, let's send via WS if connected, or assume HTTP
        # Let's use the WebSocket for "Report Issue" as requested
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send(json.dumps({
                "type": "create_ticket",
                "data": {
                    "title": title,
                    "description": description
                }
            })), self.loop)
            return True
        return False

# --- GUI Logic ---

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Omni-RMM Agent")
        self.root.geometry("300x400")
        self.root.configure(bg="#2c3e50")

        self.client = AgentClient(self)
        self.client.start()

        # Header
        tk.Label(root, text="Omni-RMM Agent", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

        # Status
        self.status_label = tk.Label(root, text="Status: Starting...", font=("Helvetica", 10), bg="#2c3e50", fg="white")
        self.status_label.pack(pady=10)

        self.status_indicator = tk.Canvas(root, width=20, height=20, bg="#2c3e50", highlightthickness=0)
        self.status_indicator.pack(pady=5)
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, fill="gray")

        # Buttons
        tk.Button(root, text="Report Issue", command=self.report_issue, width=20, height=2, bg="#e74c3c", fg="white", font=("Helvetica", 10, "bold")).pack(pady=20)

        tk.Button(root, text="Test Network", command=self.test_network, width=20, bg="#3498db", fg="white").pack(pady=5)

        # Footer
        tk.Label(root, text=f"v{AGENT_VERSION}", bg="#2c3e50", fg="#7f8c8d").pack(side=tk.BOTTOM, pady=10)

    def update_status(self, text, color):
        self.status_label.config(text=f"Status: {text}")
        self.status_indicator.itemconfig(self.status_circle, fill=color)

    def report_issue(self):
        title = simpledialog.askstring("Report Issue", "Issue Title:")
        if title:
            desc = simpledialog.askstring("Report Issue", "Description:")
            if desc:
                sent = self.client.send_ticket(title, desc)
                if sent:
                    messagebox.showinfo("Success", "Ticket reported successfully.")
                else:
                    messagebox.showerror("Error", "Could not send ticket. Check connection.")

    def test_network(self):
        try:
            response = os.system("ping -c 1 8.8.8.8") if platform.system() != "Windows" else os.system("ping -n 1 8.8.8.8")
            if response == 0:
                messagebox.showinfo("Network Test", "Network is ONLINE")
            else:
                messagebox.showwarning("Network Test", "Network appears OFFLINE")
        except Exception as e:
            messagebox.showerror("Error", f"Test failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentGUI(root)
    root.mainloop()
