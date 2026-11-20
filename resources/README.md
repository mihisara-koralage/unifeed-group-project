# Module 4 study resources

The resource backend is available at `/resources/`. The database model and its
initial migration are included because no Resource model was present in the
shared branch when this backend was implemented.

## Frontend pages

The three templates under `resources/templates/resources/` extend the shared
UniFeed shell and use `static/css/resources.css`:

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

The Resources link is included in the shared navigation. Search and category
filters use GET requests and work without JavaScript. Category links retain the
encoded search query; clearing search keeps the selected category. Empty results
offer an action to reset filters or share the first resource. Only Students see
sharing controls.

The submission page displays field and form errors while preserving entered
values. `static/js/resources.js` adds a description character counter, associates
help and errors with their fields, focuses the first invalid field, and provides
HTTP/HTTPS link validation in the browser. Server validation remains authoritative.
The confirmation page displays the destination and requires an explicit click
to open the external site in a new tab.

## Local verification

Apply the new schema with `venv\Scripts\python.exe manage.py migrate`.

Run the backend tests with:

```powershell
venv\Scripts\python.exe manage.py test resources --noinput
```

For an isolated SQLite regression run without using local PostgreSQL:

```powershell
venv\Scripts\python.exe manage.py test users feed messaging resources --settings=config.test_settings --noinput
```

The backend tests use a separate test database and cover authentication, student-only
submission, ownership assignment, CSRF, approval visibility, combined search and
category filtering, URL validation and the confirmation route. The tests in
`test_frontend.py` render the real templates and verify navigation, escaped
content, search encoding, role-specific controls, empty states, invalid forms,
successful submission, approval visibility and external-link attributes.
The backend contract tests retain test-only templates to test views independently.

The isolated suite contains 51 tests; five PostgreSQL-specific migration tests
are skipped on SQLite. Final PostgreSQL and interactive mobile browser checks
remain required before marking the whole milestone verified.
