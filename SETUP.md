# UniFeed local setup

Project: `C:\workspace\unifeed-group-project`

## Current verification status

Steps 0–8 are complete. Python 3.13.9, pip, the virtual environment, all requested
packages, six apps and folders, PostgreSQL 17.11 database `unifeed_db`, all initial
migrations, CustomUser database query, Django system checks and admin login HTTP
200 have passed. Package compatibility checks report no broken requirements.

`finish-setup.cmd` can rerun database, migration and application verification.
The existing `.env` contains the local connection settings.

Double-click `start-unifeed.cmd` to start PostgreSQL and Django, then visit
http://127.0.0.1:8000/admin/ (create a superuser first to sign in).
Close Django with Ctrl+C. PostgreSQL stays running until stopped or Windows restarts.

For a Command Prompt terminal:

```bat
cd /d C:\workspace\unifeed-group-project
venv\Scripts\activate.bat
python --version
pip --version
python manage.py check
python manage.py createsuperuser
```

For PowerShell, activation is optional. Use the virtual environment directly:

```powershell
cd C:\workspace\unifeed-group-project
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py runserver
```

The portable Python runtime is in `C:\workspace\tools\python-portable\tools`.
Keep it there: the virtual environment depends on it. The system Python command
outside this environment still points to the existing Windows Store alias.

PostgreSQL binaries: `C:\workspace\tools\pgsql\bin`.
Database data: `C:\workspace\unifeed-postgres` (outside Git).
Database log: `C:\workspace\unifeed-postgres.log` (outside its data folder).
The database listens on loopback only, port 5432, with SCRAM password authentication.
Connection credentials and a generated Django secret are in the ignored `.env`.
Never commit `.env`, the virtual environment, or the database data.

```powershell
& C:\workspace\tools\pgsql\bin\pg_ctl.exe -D C:\workspace\unifeed-postgres status
& C:\workspace\tools\pgsql\bin\pg_ctl.exe -D C:\workspace\unifeed-postgres stop -m fast
```

The requested Django packages are pinned in `requirements.txt`.
Each app has its own `forms.py`, `urls.py` and `templates/<app_name>/` folder,
matching the team's module layout. Django discovers these templates through
`APP_DIRS=True`. The root `templates/` folder remains available for shared pages.
URL files are empty placeholders; connect each module in `config/urls.py` when
its first view is ready. Models, views, forms and templates still need feature
implementation by the assigned team members.

All six apps are registered. A minimal `users.CustomUser` based on `AbstractUser`
is included because the supplied settings reference it before Module 1 creates it.
Add later user fields to that model and create a new migration.

Redis is configured at `127.0.0.1:6379` for the later messaging module.
A Redis server is not part of steps 0–8 and has not been installed here.
Real-time channel delivery needs that server before it can work.

This is a local development configuration; DEBUG is enabled.
