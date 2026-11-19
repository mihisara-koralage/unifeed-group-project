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
cannot choose or elevate roles. There are no feed templates, AJAX likes, post
composer or other Module 2 features in this change.

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
- The committed login and registration views redirect to `feed:home` after
  successful authentication. Module 2's frontend is not part of this change.
  Until that template is implemented, visit `/users/profile/` after signing in.
- A read-only check of this computer's database confirmed that it lacks `role`,
  `bio`, `avatar` and `is_verified`. The backend rewrote the already-applied
  `users/0001_initial.py`, so ordinary `migrate` cannot discover those changes.
  The backend/database developer needs to provide a proper upgrade migration
  before registration/profile actions can run on this older database. No local
  data, models or migrations were changed as part of this frontend work.
