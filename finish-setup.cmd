@echo off
cd /d "%~dp0"
venv\Scripts\python.exe finish-setup.py
if errorlevel 1 (
  echo Setup did not complete. Read the error above.
  pause
  exit /b 1
)
echo Setup verified. Run start-unifeed.cmd to start Django.
pause
