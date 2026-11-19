# Module 1: Users and authentication frontend

Implements the Module 1 template scope from the shared Claude plan, against the
committed `users` forms, views, model and named URL routes.

## Pages

- `/users/register/`: student registration with email and password validation.
- `/users/login/`: email sign-in with server-side error messages.
- `/users/profile/`: email, assigned role, verification status, bio and avatar;
  editing uses the already-committed `ProfileForm` and profile view.
- `templates/base.html`: shared account navigation, message display, static
  assets and CSRF-protected logout form.

CSS, password visibility toggles and avatar preview are scoped to accounts.
Forms submit normally and still work with JavaScript disabled. Registration
cannot choose or elevate roles. Feed and messaging are documented separately in
`FEED_MESSAGING_FRONTEND.md`; they share the account navigation and visual style.

## Validation

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test users --settings=config.test_settings
```

The test settings use an isolated in-memory SQLite database. Test accounts and
uploads are temporary; your PostgreSQL database and accounts are not modified.

## Backend integration notes

- The shared URL configuration needed the missing `include` import and the
  development-only media routes from the Module 1 plan.
- `LOGIN_URL` now points to the existing `users:login` route for protected pages.
- Login and registration now redirect to `users:profile`, as fixed upstream by
  the backend developer. The authentication tests follow this redirect through
  to a working profile page. Module 2's frontend is not required for sign-in.
- The missing `staticfiles_urlpatterns` import is fixed for DEBUG startup.
- `users/0002_reconcile_legacy_user_schema.py` repairs databases that applied the
  old username-based initial migration. After pulling, run `python manage.py
  migrate` with your virtual environment active. Fresh databases are supported
  too: columns already present are left in place.
- The repair preserves account IDs, emails, password hashes and legacy username
  values. The unused username column becomes nullable so email-only accounts can
  be registered. Existing administrator accounts retain the admin role.
- Blank or duplicate legacy emails stop the repair with an explanation; resolve
  those account emails before retrying. Accounts are never automatically merged,
  assigned fake emails or deleted. PostgreSQL upgrades run atomically.
- PostgreSQL-specific migration tests live in `users/test_migrations.py`. They
  run against Django's disposable test database; the SQLite test settings skip
  those five database-specific cases.
