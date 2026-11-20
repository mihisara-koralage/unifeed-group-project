# Module 4 resource backend

The resource backend is available at `/resources/`. The database model and its
initial migration are included because no Resource model was present in the
shared branch when this backend was implemented.

## Frontend handoff

Add these templates under `resources/templates/resources/`:

| Template | Route name | Context |
| --- | --- | --- |
| `list.html` | `resources:list` | `resources`, `categories`, `active_cat`, `search` |
| `submit.html` | `resources:submit` | `form` |
| `redirect.html` | `resources:open` | `resource` |

The directory accepts `category` and `search` query parameters. Search matches
title or description, combined with the selected category. Only approved
resources are visible, newest first. Invalid categories are ignored.

The submission form requires a signed-in Student account and a CSRF token. The
backend assigns the contributor from the session; clients cannot assign another
user or alter approval status. The model defaults to approved, as specified in
the Module 4 handoff. Administrators can hide resources using `is_approved`.

The open route renders a confirmation page rather than automatically redirecting.
Show the resource title and destination, and use an explicit link with
`target="_blank" rel="noopener noreferrer"`. Keep Django autoescaping enabled;
do not mark user-supplied titles, descriptions or URLs as safe. URLs must use
HTTP or HTTPS, pass URL validation, and contain no embedded login credentials.
No remote URL is fetched by the server.

Add `{% url 'resources:list' %}` to the shared navigation when the frontend is
ready. Until these templates are supplied, authenticated page requests will
raise `TemplateDoesNotExist`; the backend tests deliberately use test-only
templates to verify view contracts separately from the frontend.

## Local verification

Apply the new schema with `venv\Scripts\python.exe manage.py migrate`.

Run the backend tests with:

```powershell
venv\Scripts\python.exe manage.py test resources --noinput
```

The tests use a separate test database and cover authentication, student-only
submission, ownership assignment, CSRF, approval visibility, combined search and
category filtering, URL validation and the confirmation route. They do not
verify the final resource templates or external-link browser behaviour.
