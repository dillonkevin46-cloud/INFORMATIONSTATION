# Omni-RMM

Omni-RMM is a comprehensive Remote Monitoring and Management system.

## Project Structure

- `omni_rmm/`: Django project settings and configuration.
- `core/`: Core functionality, including User management.
- `devices/`: Device management, RMM Agent communication, and monitoring.
- `tickets/`: Ticketing system.
- `knowledge_base/`: Knowledge Base (Wiki).
- `checklists/`: Forms and checklists.
- `agent/`: Source code for the RMM Agent (Client).

## Setup (Server)

1. Install dependencies:
   ```bash
   pip install django channels daphne djangorestframework psycopg2-binary websockets psutil
   ```

2. Run migrations (Essential):
   ```bash
   python manage.py migrate
   ```

3. Start the server (using Daphne for WebSocket support):
   ```bash
   daphne -p 8000 omni_rmm.asgi:application
   ```

   **Alternatively, use the provided helper scripts:**
   - Windows: `start_server.bat`
   - Linux/Mac: `./start_server.sh`

## Setup (Agent)

1. Navigate to the `agent/` directory (or distribute `agent/main.py`).
2. Install agent dependencies:
   ```bash
   pip install websockets psutil pystray Pillow mss
   ```
3. Run the agent:
   ```bash
   python agent/main.py --server wss://localhost:8000/ws/agent/
   ```
   Or set `RMM_SERVER_URL` environment variable.

   *Note: For local development without SSL, use `ws://` instead of `wss://`.*

## Features Implemented

- **Remote Control**: Live screen viewing and terminal command execution.
- **System Tray Icon**: Quick actions for reporting issues and network tests.
- **Automation**: Auto-ticket creation from checklists and email notifications on ticket closure.
- **Dashboard**: Real-time telemetry charts (CPU/RAM history).
- **Database Schema**: Complete Django models for Users, Devices, Tickets, Assets, KB, Checklists.
- **WebSocket Communication**: Real-time bidirectional communication.

## Environment Variables

- `DB_ENGINE`: Set to `postgresql` to use PostgreSQL.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database connection details.
