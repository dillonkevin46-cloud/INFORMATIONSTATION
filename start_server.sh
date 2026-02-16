#!/bin/bash
echo "Running migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "Migration failed!"
    exit 1
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Omni-RMM Server..."
daphne -p 8000 omni_rmm.asgi:application
