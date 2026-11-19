# Feed and messaging frontend

## Pages and actions

- `/`: student post composer, image preview/upload, latest posts, AJAX likes,
  Message links to other authors, hashtag links and copy-link actions.
- `/tag/<name>/`: posts in a hashtag conversation. Both feed pages have client
  search and filters for all posts, your posts and photo posts. Filters apply to
  the posts already rendered on the current page.
- `/messages/`: real conversations, last-message previews, unread badges and
  conversation search. Start a new conversation from a feed post's Message link.
- `/messages/<user_id>/`: persisted history, live messages, typing indicators,
  connection/reconnect feedback, preserved drafts and per-viewer message hiding.
- Shared navigation now links Feed, Messages and My profile. Account pages retain
  their original layout and authentication behavior.

The backend's routes, models, form fields and WebSocket payloads are preserved.
Templates use `{% endif %}`. Chat overrides the shared notification block because
its `messages` context is chat history, not Django's flash-message collection.
Messages and posts are escaped; new socket messages are inserted as text.
Message hiding uses POST and CSRF, and respects sender/recipient deletion flags.

## Run locally

Install `requirements.txt` into your virtual environment and apply migrations.
Use `start-unifeed.cmd` on Ashen's existing local installation, or on another
computer with PostgreSQL already running:

```powershell
python manage.py migrate
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

Live chat requires an ASGI server; the ordinary WSGI `runserver` does not support
these WebSockets. `DEBUG=True` enables the existing development static/media
routes. Daphne does not reload Python code automatically; restart after edits.

The default channel backend is Redis at `127.0.0.1:6379`. For local development
without Redis, set `CHANNEL_BACKEND=memory` in your ignored `.env`, with DEBUG
enabled. This option is restricted to development and **one ASGI process**.
Use Redis for multiple processes or deployment. This computer uses memory mode
for its single local server. No user account or sample posts are added to the
real database by the frontend work.

## Verify

```powershell
python manage.py check
python manage.py test users feed messaging --settings=config.test_settings
```

Tests use a disposable database and in-memory channels for messaging. The
PostgreSQL migration tests additionally run with PostgreSQL test settings.

Message delivery is confirmed by the backend's echoed event. If a connection is
lost before that confirmation, refresh to inspect history before resending; the
frontend does not automatically resend a possibly delivered message. Live chat
history marks existing read messages as Seen, but does not invent live read
receipts or the other person's online status.
