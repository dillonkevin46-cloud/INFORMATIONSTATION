@echo off
echo Running migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo Migration failed!
    exit /b %ERRORLEVEL%
)

echo Collecting static files...
python manage.py collectstatic --noinput

echo Starting Omni-RMM Server...
daphne -p 8000 omni_rmm.asgi:application
