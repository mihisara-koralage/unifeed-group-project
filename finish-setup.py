"""Complete PostgreSQL initialization and verify the local Django setup."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import socket

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent
BIN = Path(r'C:\workspace\tools\pgsql\bin')
DATA = Path(r'C:\workspace\unifeed-postgres')
values = dotenv_values(ROOT / '.env')
env = os.environ.copy()
env['PGPASSWORD'] = values['DATABASE_PASSWORD']


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env, check=True, **kwargs)


if not (DATA / 'global' / 'pg_control').exists():
    if DATA.exists() and any(DATA.iterdir()):
        raise SystemExit(f'Incomplete database directory: {DATA}. Preserve it and choose a fresh DATA directory before retrying.')
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, dir=ROOT, prefix='.pg-password-', suffix='.tmp') as handle:
        handle.write(values['DATABASE_PASSWORD'])
        password_path = Path(handle.name)
    try:
        run(BIN / 'initdb.exe', '-D', DATA, '-U', 'postgres', '-E', 'UTF8', '--locale=C', '--auth=scram-sha-256', '-c', 'max_connections=25', '-c', 'shared_buffers=16MB', f'--pwfile={password_path}')
    finally:
        password_path.unlink(missing_ok=True)
    with (DATA / 'postgresql.conf').open('a', encoding='utf-8') as handle:
        handle.write("\nlisten_addresses = '127.0.0.1'\nport = 5432\n")

try:
    with socket.create_connection((values['DATABASE_HOST'], int(values['DATABASE_PORT'])), timeout=3):
        pass
except OSError:
    run(BIN / 'pg_ctl.exe', '-D', DATA, '-l', DATA.parent / 'unifeed-postgres.log', '-w', 'start')

import psycopg2
connection = psycopg2.connect(host=values['DATABASE_HOST'], port=values['DATABASE_PORT'], user=values['DATABASE_USER'], password=values['DATABASE_PASSWORD'], dbname='postgres', connect_timeout=10)
connection.autocommit = True
with connection.cursor() as cursor:
    cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (values['DATABASE_NAME'],))
    if cursor.fetchone() is None:
        from psycopg2 import sql
        cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(values['DATABASE_NAME'])))
connection.close()
run(sys.executable, 'manage.py', 'migrate')
run(sys.executable, 'manage.py', 'check', '--database', 'default')
run(sys.executable, '-m', 'pip', 'check')

sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
from django.contrib.auth import get_user_model
from django.test import Client
with connection.cursor() as cursor:
    cursor.execute('SELECT current_database()')
    assert cursor.fetchone()[0] == values['DATABASE_NAME']
get_user_model().objects.count()
assert Client(HTTP_HOST='localhost').get('/admin/login/').status_code == 200
print('PASS: PostgreSQL, migrations, CustomUser query, Django check, package compatibility and admin HTTP 200.')
