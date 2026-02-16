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

2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Start the server (using Daphne for WebSocket support):
   ```bash
   daphne -p 8000 omni_rmm.asgi:application
   ```

## Setup (Agent)

1. Navigate to the `agent/` directory (or distribute `agent/main.py`).
2. Run the agent:
   ```bash
   python agent/main.py --server ws://localhost:8000/ws/agent/
   ```
   Or set `RMM_SERVER_URL` environment variable.

## Features Implemented

- **Database Schema**: Complete Django models for Users, Devices, Tickets, Assets, KB, Checklists.
- **WebSocket Communication**: Real-time bidirectional communication between Server and Agent.
- **Agent Logic**: Auto-discovery, Heartbeat (CPU/RAM/Disk usage), Command execution framework.
- **Modular Architecture**: Separated apps for different functionalities.

## Environment Variables

- `DB_ENGINE`: Set to `postgresql` to use PostgreSQL.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database connection details.
