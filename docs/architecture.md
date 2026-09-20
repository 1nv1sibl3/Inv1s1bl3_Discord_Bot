# Inv1s1bl3 Bot — System Architecture

## 1. High-Level Architectural Overview

Inv1s1bl3 Bot is organized as a modular, decoupled application combining an asynchronous Discord bot process with a Flask-powered web management dashboard, both sharing an asynchronous database access layer built on **SQLAlchemy 2.0**.

```
                           +---------------------------+
                           |    Discord Gateway API    |
                           +-------------+-------------+
                                         |  Websockets / REST
                                         v
+------------------------+      +---------------------------+
|   Flask Web Dashboard  |      |     discord.py 2.x Bot    |
|   (OAuth2, Guild Mgmt) |      |     (Commands & Cogs)     |
+-----------+------------+      +-------------+-------------+
            |                                 |
            +----------------+  +-------------+
                             |  |
                             v  v
            +-----------------------------------+
            |    SQLAlchemy 2.0 Async Layer     |
            |     (CRUD Services & Models)      |
            +-----------------+-----------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+     +---------------+     +---------------+
| SQLite (dev)  |     |  PostgreSQL   |     | MySQL/MariaDB |
|  aiosqlite    |     |    asyncpg    |     |    aiomysql   |
+---------------+     +---------------+     +---------------+
```

---

## 2. Directory Layout & Module Responsibilities

```
inv1s1bl3-bot-public/
├── alembic/                # Versioned database migration scripts
├── assets/                 # Static data (market catalog, company limits) & media
├── docs/                   # Engineering & design documentation
├── scripts/                # Standalone operator scripts (run_bot, run_dashboard, init_db)
├── src/
│   ├── config/             # Environment parsing, type-safe settings validation
│   ├── database/           # SQLAlchemy DeclarativeBase models, session manager, CRUD
│   │   ├── crud/           # Isolated data-access services (users, economy, business, server, count)
│   │   ├── models.py       # Cross-database relational models
│   │   └── session.py      # AsyncEngine & async_sessionmaker factory
│   ├── bot/                # Discord bot client implementation
│   │   ├── bot.py          # Custom commands.Bot subclass, prefix resolution, error hooks
│   │   ├── cogs/           # Modular bot extensions (admin, basic, business, economy, etc.)
│   │   ├── games/          # Guess A Word (GAW) session manager and engine
│   │   └── utils/          # Standardized embeds, permissions checks, async API clients
│   ├── web/                # Flask dashboard & Discord OAuth2
│   │   ├── app.py          # Application factory, session security, template filters
│   │   ├── auth.py         # Discord OAuth2 flow with CSRF state validation
│   │   ├── routes.py       # Endpoints for landing, dashboard, server configuration
│   │   ├── static/         # Modern Discord dark-theme CSS & JS
│   │   └── templates/      # Jinja2 responsive templates
│   └── __main__.py         # Unified CLI entrypoint (--mode bot|web|all|init-db)
└── tests/                  # Automated pytest test suite
```

---

## 3. Key Design Principles

1. **Dialect-Agnostic Database Layer**: No raw vendor SQL or PostgreSQL-specific arrays. All database interactions utilize SQLAlchemy 2.0 async ORM constructs, enabling zero-configuration SQLite for local development and asyncpg/aiomysql for production.
2. **Non-Blocking Async Event Loop**: All external API integrations (NASA, Joke, PokeAPI, Wikipedia) leverage an asynchronous `aiohttp.ClientSession`, preventing network delays from freezing the Discord bot gateway.
3. **Session & OAuth2 Hardening**: Web dashboard OAuth2 transactions implement cryptographic `state` parameters to thwart CSRF attacks. Session cookies are enforced with `HttpOnly` and `SameSite=Lax`.
4. **Decoupled Deployment Modes**: The application can run as a standalone Discord bot (`--mode bot`), a standalone web dashboard (`--mode web`), or as a combined development server (`--mode all`).
