@echo off
cd /d "%~dp0"
if not exist "C:\workspace\unifeed-postgres\global\pg_control" (
  echo Run finish-setup.cmd first to initialize and verify PostgreSQL.
  pause
  exit /b 1
)
"C:\workspace\tools\pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5432 -q
if errorlevel 1 (
  "C:\workspace\tools\pgsql\bin\pg_ctl.exe" -D "C:\workspace\unifeed-postgres" -l "C:\workspace\unifeed-postgres.log" -w start
  if errorlevel 1 exit /b 1
)
call venv\Scripts\activate.bat
python manage.py check
if errorlevel 1 exit /b 1
if not exist "venv\Scripts\daphne.exe" (
  echo Install the project packages first: venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
echo Open http://127.0.0.1:8000/ in your browser. Keep this window open for live chat.
venv\Scripts\daphne.exe -b 127.0.0.1 -p 8000 config.asgi:application
