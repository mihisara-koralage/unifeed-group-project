# UniFeed – University Community Platform

UniFeed is a university community platform designed to connect university students through social networking, real-time messaging, educational resource sharing, event management and a student marketplace.

This document explains how to install, configure and run the UniFeed project on a local Windows computer.

---

# 1. Project Features

The UniFeed platform consists of the following modules:

1. User Authentication
2. Social Feed
3. Real-Time Messaging
4. Study Material and Resource Sharing
5. Event Aggregator
6. Marketplace

# 2. Technologies Used

## Backend
- Python
- Django
- Django REST Framework
- Django Channels
- WebSockets

## Frontend
- HTML
- CSS
- JavaScript

## Database
- PostgreSQL

## Development Tools
- Git
- GitHub
- Visual Studio Code
- PowerShell

# 3. Software Requirements

Install the following software before setting up the project.

| Software | Purpose |
|---|---|
| Python | Run the Django backend |
| Git | Clone and manage the repository |
| Visual Studio Code | Edit project files |
| PostgreSQL | Database management |
| pgAdmin | Manage PostgreSQL databases (optional) |
| Redis | WebSocket/channel layer support, if configured |
| GitHub Desktop | Graphical Git management (optional) |

Official download pages:

- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads
- VS Code: https://code.visualstudio.com/
- PostgreSQL: https://www.postgresql.org/download/windows/
- Redis: https://redis.io/downloads/

# 4. Verify Software Installation

Open PowerShell.

Check Python:

```powershell
python --version
```

Check Git:

```powershell
git --version
```

Check PostgreSQL (if its command-line tools are added to PATH):

```powershell
psql --version
```

# 5. Clone the GitHub Repository

Open PowerShell and navigate to the location where you want to store the project.

Example:

```powershell
cd D:\
```

Clone the repository:

```powershell
git clone https://github.com/mihisara-koralage/unifeed-group-project.git
```

Navigate into the project:

```powershell
cd unifeed-group-project
```

# 6. Open the Project in Visual Studio Code

Run:

```powershell
code .
```

Alternatively:

1. Open Visual Studio Code.
2. Select File.
3. Select Open Folder.
4. Choose the unifeed-group-project folder.

# 7. Create a Python Virtual Environment

A virtual environment keeps the project's Python dependencies separate from other Python projects.

Create the environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Activate again:

```powershell
.venv\Scripts\Activate.ps1
```

Successful activation should display:

```text
(.venv)
```

at the beginning of the terminal line.

# 8. Upgrade pip

Run:

```powershell
python -m pip install --upgrade pip
```

# 9. Install Project Dependencies

The requirements.txt file contains the Python packages required by UniFeed.

Install them using:

```powershell
python -m pip install -r requirements.txt
```

Wait until the installation finishes.

Verify Django:

```powershell
python -m django --version
```

# 10. Configure Environment Variables

The repository contains an `.env.example` file.

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open the file:

```powershell
notepad .env
```

Review the available variables.

Configure the database credentials and other settings according to your local installation.

For PostgreSQL, the configuration may include:

- DATABASE_HOST
- DATABASE_NAME
- DATABASE_USER
- DATABASE_PASSWORD
- DATABASE_PORT
- DEBUG
- SECRET_KEY

Use the exact variable names expected by the project's settings.py.

Important:

- Never upload your actual `.env` file.
- Never share database passwords or secret keys.
- Keep `.env.example` updated with safe placeholder values.

# 11. PostgreSQL Database Setup

If the project is configured to use PostgreSQL, install PostgreSQL and start its database service.

Open pgAdmin or PostgreSQL command-line tools.

Create a database for UniFeed.

Example using SQL:

```sql
CREATE DATABASE unifeed_testing_db;
```

Configure the `.env` file with the database name and your PostgreSQL credentials.

Example:

```text
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
DATABASE_NAME=unifeed_testing_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_local_password
```

Use the actual variable names required by settings.py.

Do not commit real credentials.

# 12. Run Django System Checks

Before starting the application, check the project configuration:

```powershell
python manage.py check
```

If no errors are found, Django should display:

```text
System check identified no issues.
```

# 13. Apply Database Migrations

Run:

```powershell
python manage.py migrate
```

This creates or updates the database tables required by the application.

If you modify Django models and need new migration files, run:

```powershell
python manage.py makemigrations
```

Then:

```powershell
python manage.py migrate
```

Do not generate new migrations unnecessarily.

# 14. Create an Administrator Account

To create a Django superuser:

```powershell
python manage.py createsuperuser
```

Follow the terminal instructions.

The administrator can access the Django administration panel if enabled.

# 15. Configure Redis (If Required)

UniFeed uses Django Channels for real-time messaging.

If the project's settings.py configures Redis as the channel layer backend, Redis must be installed and running.

Start the Redis service using the method appropriate for your installation.

Check that Redis is accessible:

```powershell
redis-cli ping
```

Expected response:

```text
PONG
```

If the project uses an in-memory channel layer for local development, Redis may not be necessary.

Check config/settings.py before configuring Redis.

# 16. Run the Development Server

Activate the virtual environment if it is not already active:

```powershell
.venv\Scripts\Activate.ps1
```

Start the Django development server:

```powershell
python manage.py runserver
```

Expected output:

```text
Starting development server at http://127.0.0.1:8000/
```

Open your browser:

http://127.0.0.1:8000/

The UniFeed application should now load.

Note: Django's standard runserver uses the WSGI development server. If testing WebSocket functionality, use the project's configured ASGI development setup.

# 17. Application URLs

The following are known application routes:

| Feature | URL |
|---|---|
| Home | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/users/login/ |
| Registration | http://127.0.0.1:8000/users/register/ |
| Profile | http://127.0.0.1:8000/users/profile/ |
| Messages | http://127.0.0.1:8000/messages/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |

Some routes may depend on the currently integrated modules.

# 18. Run Automated Tests

Run the complete Django test suite:

```powershell
python manage.py test
```

Check project configuration:

```powershell
python manage.py check
```

These commands help identify application errors and failed automated tests.

# 19. Project Folder Structure

```text
unifeed-group-project/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── users/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── feed/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   └── tests.py
│
├── messaging/
│   ├── migrations/
│   ├── templates/
│   ├── consumers.py
│   ├── models.py
│   └── views.py
│
├── resources/
├── events/
├── marketplace/
│
├── static/
├── templates/
├── media/
│
├── requirements.txt
├── .env.example
├── manage.py
└── README.md
```

# 20. Git and GitHub Workflow

Check the current branch:

```powershell
git branch
```

Check repository changes:

```powershell
git status
```

Download updated remote information:

```powershell
git fetch origin
```

Switch to your working branch:

```powershell
git switch "your Brach"
```

Get the latest changes from the main branch:

```powershell
git merge origin/main
```

Review changes:

```powershell
git status
```

Stage your changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Describe your changes"
```

Push your branch:

```powershell
git push origin tester-Akeesha
```

Always review changes before committing.

# 21. Common Problems and Solutions

## Problem 1: Django Module Not Found

Error:

```text
ModuleNotFoundError: No module named 'django'
```

Solution:

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install requirements again:

```powershell
python -m pip install -r requirements.txt
```

## Problem 2: PowerShell Execution Policy Error

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Activate the environment again.

## Problem 3: Database Connection Error

Check:

- PostgreSQL service is running.
- Database exists.
- Database name is correct.
- Username and password are correct.
- Environment variables match settings.py.

Then run:

```powershell
python manage.py migrate
```

## Problem 4: Port Already in Use

Run the application using another port:

```powershell
python manage.py runserver 8001
```

Open:

http://127.0.0.1:8001/

## Problem 5: Static Files Not Loading

Check:

- STATIC_URL configuration.
- Static file locations.
- Browser console errors.
- Django server output.

## Problem 6: WebSocket Connection Failed

Check:

- ASGI configuration.
- Django Channels installation.
- Redis availability if configured.
- WebSocket routing.
- Browser console errors.

# 22. Stop the Development Server

To stop the Django development server, press:

```text
CTRL + C
```

in the terminal where the server is running.

# 23. Security and Development Notes

- Never upload `.env` files.
- Never upload passwords or private credentials.
- Do not commit virtual environment folders.
- Keep requirements.txt updated.
- Apply migrations after pulling changes that introduce new migration files.
- Use separate Git branches for individual contributions.
- Test changes before pushing them to GitHub.
- Do not use the Django development server for production deployment.

# 24. GitHub Repository

Repository:

https://github.com/mihisara-koralage/unifeed-group-project

---

**UniFeed – Connecting University Communities**