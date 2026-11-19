"""Upgrade databases that applied the original username-based 0001.

0001 was later replaced by the email/role version in Git. Django cannot detect
that an already-applied migration changed. Inspect the actual table so this
repair also runs safely on fresh databases that already have the newer schema.
"""
from django.db import migrations, models


def reconcile_user_schema(apps, schema_editor):
    User = apps.get_model('users', 'CustomUser')
    connection = schema_editor.connection
    table = User._meta.db_table
    quote = schema_editor.quote_name
    with connection.cursor() as cursor:
        columns = {
            field.name: field
            for field in connection.introspection.get_table_description(cursor, table)
        }
        constraints = connection.introspection.get_constraints(cursor, table)
        # Do not invent emails or silently merge accounts when adding uniqueness.
        cursor.execute(
            f'SELECT COUNT(*) FROM {quote(table)} '
            f'WHERE {quote("email")} IS NULL OR TRIM({quote("email")}) = %s', ['']
        )
        if cursor.fetchone()[0]:
            raise RuntimeError(
                'User upgrade stopped: existing accounts have blank emails. '
                'Assign each account its real email before retrying migrate. '
                'No accounts have been deleted.'
            )
        cursor.execute(
            f'SELECT COUNT(*) FROM {quote(table)} GROUP BY {quote("email")} '
            'HAVING COUNT(*) > 1 LIMIT 1'
        )
        if cursor.fetchone():
            raise RuntimeError(
                'User upgrade stopped: existing accounts share an email. '
                'Resolve duplicate emails before retrying migrate. '
                'No accounts have been merged or deleted.'
            )

    legacy_username = columns.get('username')
    if legacy_username and not legacy_username.null_ok and connection.vendor != 'postgresql':
        raise RuntimeError(
            'The legacy username-table upgrade requires PostgreSQL, the project database. '
            'Fresh databases with the current initial migration do not need this repair.'
        )

    added_role = 'role' not in columns
    for name in ('role', 'bio', 'avatar', 'is_verified'):
        if name not in columns:
            schema_editor.add_field(User, User._meta.get_field(name))

    if added_role:
        # Preserve the meaning of existing administrator accounts.
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE {quote(table)} SET {quote("role")} = %s '
                f'WHERE {quote("is_superuser")} = %s', ['admin', True]
            )

    email_unique = any(
        constraint.get('unique') and constraint.get('columns') == ['email']
        for constraint in constraints.values()
    )
    if not email_unique:
        old_email = models.EmailField(max_length=254, blank=True)
        old_email.set_attributes_from_name('email')
        old_email.model = User
        schema_editor.alter_field(User, old_email, User._meta.get_field('email'))

    if legacy_username and not legacy_username.null_ok:
        # Keep legacy names as historical data, but allow new email-only users.
        # Dropping the column would permanently discard old usernames.
        schema_editor.execute(
            f'ALTER TABLE {quote(table)} ALTER COLUMN {quote("username")} DROP NOT NULL'
        )


class Migration(migrations.Migration):
    atomic = True
    dependencies = [('users', '0001_initial')]
    operations = [
        # 0001's state already describes the desired model. No state changes.
        # Reversing this repair leaves its data and declared columns intact.
        migrations.RunPython(reconcile_user_schema, reverse_code=migrations.RunPython.noop),
    ]
