@echo off
echo Running migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo Migration failed!
    exit /b %ERRORLEVEL%
)

echo Starting Omni-RMM Server...
daphne -p 8000 omni_rmm.asgi:application
