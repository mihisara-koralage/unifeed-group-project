"""Exercise the legacy schema repair on PostgreSQL, not a SQLite approximation."""
from importlib import import_module
from unittest import skipUnless

from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.db.migrations.state import ProjectState
from django.test import TransactionTestCase


@skipUnless(connection.vendor == 'postgresql', 'Legacy project databases use PostgreSQL.')
class LegacyUserSchemaTests(TransactionTestCase):
    table = 'users_upgrade_test_fixture'

    def setUp(self):
        if not str(connection.settings_dict['NAME']).startswith('test_'):
            raise RuntimeError('Schema fixtures must only run in a Django test database.')
        state = ProjectState.from_apps(apps)
        state.alter_model_options('users', 'customuser', {'db_table': self.table})
        self.historical_apps = state.apps
        self.User = self.historical_apps.get_model('users', 'CustomUser')
        self.repair = import_module('users.migrations.0002_reconcile_legacy_user_schema').reconcile_user_schema
        with connection.cursor() as cursor:
            cursor.execute(f'''
                CREATE TABLE "{self.table}" (
                    id BIGSERIAL PRIMARY KEY,
                    password VARCHAR(128) NOT NULL DEFAULT '',
                    last_login TIMESTAMPTZ NULL,
                    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL DEFAULT '',
                    last_name VARCHAR(150) NOT NULL DEFAULT '',
                    email VARCHAR(254) NOT NULL DEFAULT '',
                    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def tearDown(self):
        with connection.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS "{self.table}"')
        super().tearDown()

    def insert_legacy(self, username='legacy-name', email='legacy@example.test', admin=False):
        with connection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO "{self.table}" (username,email,password,is_superuser) VALUES (%s,%s,%s,%s)',
                [username, email, 'encoded-password-preserved', admin],
            )

    def apply_repair(self):
        with connection.schema_editor() as editor:
            self.repair(self.historical_apps, editor)

    def column_names(self):
        with connection.cursor() as cursor:
            return {field.name for field in connection.introspection.get_table_description(cursor, self.table)}

    def test_upgrade_preserves_accounts_passwords_and_old_names(self):
        self.insert_legacy(admin=True)
        self.apply_repair()
        user = self.User.objects.get(email='legacy@example.test')
        self.assertEqual(user.password, 'encoded-password-preserved')
        self.assertEqual(user.role, 'admin')
        self.assertEqual(user.bio, '')
        self.assertFalse(user.is_verified)
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT username FROM "{self.table}" WHERE id=%s', [user.pk])
            self.assertEqual(cursor.fetchone()[0], 'legacy-name')
        new_user = self.User.objects.create(email='new@example.test')
        self.assertEqual(new_user.role, 'student')
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.User.objects.create(email='legacy@example.test')

    def test_reapplying_repair_preserves_new_profile_values(self):
        self.insert_legacy()
        self.apply_repair()
        self.User.objects.filter(email='legacy@example.test').update(role='page', bio='Keep this bio', is_verified=True)
        self.apply_repair()
        user = self.User.objects.get(email='legacy@example.test')
        self.assertEqual(user.bio, 'Keep this bio')
        self.assertEqual(user.role, 'page')
        self.assertTrue(user.is_verified)

    def test_duplicate_emails_fail_without_deleting_accounts(self):
        self.insert_legacy(username='one')
        self.insert_legacy(username='two')
        with self.assertRaisesMessage(RuntimeError, 'share an email'):
            self.apply_repair()
        self.assertNotIn('role', self.column_names())
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM "{self.table}"')
            self.assertEqual(cursor.fetchone()[0], 2)

    def test_blank_email_stops_before_schema_changes(self):
        self.insert_legacy(email='')
        with self.assertRaisesMessage(RuntimeError, 'blank emails'):
            self.apply_repair()
        self.assertNotIn('role', self.column_names())

    def test_partially_upgraded_roles_are_not_overwritten(self):
        self.insert_legacy()
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER TABLE "{self.table}" ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT %s', ['page'])
        self.apply_repair()
        user = self.User.objects.get(email='legacy@example.test')
        self.assertEqual(user.role, 'page')
        self.assertEqual(user.bio, '')
