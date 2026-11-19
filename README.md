# unifeed-group-project

UniFeed is a Django campus community app with email-based accounts, a social
feed and live messaging. Each module keeps its own templates alongside its
backend files. Shared layout and styles live in `templates/` and `static/`.

- Account pages: `/users/register/`, `/users/login/`, `/users/profile/`.
- Campus feed: `/`, with posts, image uploads, likes and hashtag conversations.
- Messages: `/messages/`, with real-time chat and per-user message hiding.

See `MODULE1_FRONTEND.md` for accounts and database upgrade notes, and
`FEED_MESSAGING_FRONTEND.md` for feed/chat setup and testing. Install
`requirements.txt`, configure your ignored `.env` from `.env.example`, create
your PostgreSQL database and run `python manage.py migrate`.

Run the app with `daphne -b 127.0.0.1 -p 8000 config.asgi:application` while your
virtual environment is active. For a single local server without Redis, enable
DEBUG and set `CHANNEL_BACKEND=memory` in `.env`. Multi-process environments use
the default Redis channel backend. Never commit `.env` or the virtual environment.

On Ashen's configured computer, `start-unifeed.cmd` starts PostgreSQL and Daphne.
Those launcher database paths are local to that installation.
