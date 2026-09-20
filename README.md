# Inv1s1bl3 Discord Bot 🤖

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.4.0%2B-blueviolet.svg?logo=discord&logoColor=white)](https://github.com/Rapptz/discord.py)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)


> **Legacy Open-Source Project**:  
> Inv1s1bl3 Bot was originally created ~4 years ago as a personal learning project to explore Python, Discord bots, Flask web development, databases, and third-party APIs.  
> The codebase has been fully refactored, modernized, and open-sourced under the MIT license to preserve its history and original features while adhering to modern Python 3.10+, discord.py 2.x, and async SQLAlchemy standards.

---

## 📑 Table of Contents
- [✨ Key Features](#-key-features)
- [🏛️ Architecture Overview](#️-architecture-overview)
- [📦 Prerequisites](#-prerequisites)
- [🚀 Quick Start & Installation](#-quick-start--installation)
- [⚙️ Configuration (.env)](#️-configuration-env)
- [🤖 Discord Developer Portal Setup](#-discord-developer-portal-setup)
- [🎮 Running the Application](#-running-the-application)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [📁 Project Structure](#-project-structure)
- [🔒 Security & Credential Hygiene](#-security--credential-hygiene)
- [🤝 Contributing & Migrations](#-contributing--migrations)
- [📜 License](#-license)

---

## ✨ Key Features

### 1. Bot Modules & Cogs (`src/bot/cogs/`)
- **Admin**: Safe dynamic extension reloading (`load`, `unload`, `reload`), application command tree syncing (`sync`), and non-destructive system diagnostics.
- **Basic**: Core utility commands (`ping`, `invite`, `poke`, `echo`, and fun text styling like `owo`).
- **Business**: A venture capital and startup simulation game:
  - Register businesses (`bregister`)
  - Create and sell products (`bproduct`, `bsell`)
  - Hire and fire guild members as employees (`hire`, `fire`)
  - Manage company payroll and company valuation (`bstatus`, `binfo`, `bpay`)
- **Economy & Leveling**:
  - Global user profiles, XP progression, and dynamic level calculation (`rank`, `leaderboard`)
  - Banking system with wallets, deposits, withdrawals, and user-to-user transfers (`balance`, `deposit`, `withdraw`, `transfer`)
  - Daily reward streak (`daily`)
  - Interactive item shop and personal inventory (`market`, `buy`, `inventory`, `use`)
- **Fun**:
  - Astronomy picture of the day via NASA APOD API
  - Quick Wikipedia article summaries
  - Yes/No decision engine with animated GIFs
  - Pokémon Pokedex lookups
  - Random dad jokes, Truth or Dare, and Boredom activity suggestions
  - AI chat assistant with local intelligent fallbacks
- **Gamble**:
  - Discord UI interactive button views for Coin Flip and Dice Roll
  - Dynamic payouts and wallet integration
- **Games**:
  - Interactive Discord UI Rock-Paper-Scissors (`rps`)
  - Guess-a-Word (`gaw`) word puzzle with letter hints and real-time masking
  - Server Counting Game: dedicated counting channels with persistence, streak tracking, and mistake detection
  - 8ball, riddles, word unscrambler, and math ecogame
- **Moderator**:
  - Native Discord member timeouts (`timeout` / `untimeout` using `member.timeout`)
  - Member moderation: `kick`, `ban`, `unban` (async ban list iteration)
  - Channel management: `lock`, `unlock`, bulk message purge (`clear`)
  - Role management (`giverole`, `removerole`)
  - Guild announcements (`announce`) and dynamic server prefix customization (`setprefix`)
- **Server**:
  - Guild statistics and member breakdown (`serverinfo`)
  - Detailed user profile inspection (`whois` / `userinfo`)
  - Bot resource telemetry (`botstats`)
- **MV**: Multimedia voice playback integration stub.

### 2. Modern Web Dashboard (`src/web/`)
- **Discord OAuth2 Login**: Secure user authentication with state-based CSRF protection.
- **Guild Permissions**: Automatically filters servers where the user possesses `MANAGE_GUILD` permissions.
- **Live Server Management**:
  - Dynamic command prefix configuration per guild
  - Welcome and Leave notification channels and custom messages
- **Discord Dark Theme**: Fully responsive CSS layout matching Discord's native design system.

### 3. Database Layer (`src/database/`)
- **SQLAlchemy 2.0 Async ORM**: Full async operations via `AsyncSession`.
- **Dialect Agnostic**: Seamlessly switches between SQLite (`aiosqlite`), PostgreSQL (`asyncpg`), and MySQL (`aiomysql`) via the connection URL.
- **Alembic Migrations**: Structured database schema versioning.

---

## 🏛️ Architecture Overview

```
+--------------------------------------------------------------------+
|                         Inv1s1bl3 Platform                         |
+---------------------------------+----------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
|   Discord Bot (2.x)   |                   |  Flask Web Dashboard  |
|  - Subclassed Bot     |                   |  - Discord OAuth2     |
|  - Dynamic Prefix     |                   |  - CSRF Protection    |
|  - Modern Cogs & Views|                   |  - Guild Management   |
|  - Async API Clients  |                   |  - Server Config UI   |
+-----------+-----------+                   +-----------+-----------+
            |                                           |
            +---------------------+---------------------+
                                  |
                                  v
            +-------------------------------------------+
            |      Async CRUD Layer (src/database/)     |
            |     - Users & XP   - Economy & Market     |
            |     - Business     - Guild Settings       |
            +---------------------+---------------------+
                                  |
                                  v
            +-------------------------------------------+
            |         SQLAlchemy 2.0 Async ORM          |
            |   (SQLite / PostgreSQL / MySQL / MariaDB) |
            +-------------------------------------------+
```

---

## 📦 Prerequisites

- **Python**: 3.10, 3.11, or 3.12
- **Database**: SQLite (default, zero-config) or PostgreSQL 14+ / MySQL 8+
- **Git**

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/username/inv1s1bl3-bot.git
cd inv1s1bl3-bot
```

### 2. Create a Virtual Environment
```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your credentials:
```bash
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Edit `.env` using your preferred editor and provide your Discord Bot Token and OAuth2 secrets.

### 5. Initialize the Database
```bash
python -m src --mode init-db
# or run Alembic migrations:
alembic upgrade head
```

---

## ⚙️ Configuration (.env)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | **Yes** | — | Discord Bot Token from Developer Portal |
| `DISCORD_CLIENT_ID` | For Dashboard | — | Discord Application ID |
| `DISCORD_CLIENT_SECRET` | For Dashboard | — | Discord Application OAuth2 Client Secret |
| `DISCORD_REDIRECT_URI` | For Dashboard | `http://localhost:5000/callback` | OAuth2 Callback URL |
| `DATABASE_URL` | Optional | `sqlite+aiosqlite:///./data/bot.db` | SQLAlchemy 2.0 async database URL |
| `DEFAULT_PREFIX` | Optional | `.` | Default command prefix |
| `OWNER_IDS` | Optional | `[]` | Comma-separated list of Discord user IDs with bot owner privileges |
| `NASA_API_KEY` | Optional | `DEMO_KEY` | NASA API key for astronomy pictures |
| `GIPHY_API_KEY` | Optional | — | GIPHY API key for search/GIFs |
| `OPENAI_API_KEY` | Optional | — | OpenAI API key for AI assistant features |
| `FLASK_SECRET_KEY` | Optional | Random | Flask session secret key |
| `WEB_HOST` | Optional | `0.0.0.0` | Dashboard bind host |
| `WEB_PORT` | Optional | `5000` | Dashboard bind port |
| `DEBUG` | Optional | `false` | Enable verbose debug logging |

---

## 🤖 Discord Developer Portal Setup

1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and provide a name.
3. Under **Bot**:
   - Click **Reset Token** to copy your `DISCORD_TOKEN`.
   - Scroll down to **Privileged Gateway Intents** and enable:
     - ✅ **Server Members Intent** (required for user moderation and leveling)
     - ✅ **Message Content Intent** (required for prefix commands and counting game)
4. Under **OAuth2**:
   - Copy your **Client ID** (`DISCORD_CLIENT_ID`) and **Client Secret** (`DISCORD_CLIENT_SECRET`).
   - Add your Redirect URL: `http://localhost:5000/callback` (or your production URL).
5. Generate Bot Invite URL:
   - Go to **OAuth2 -> URL Generator**.
   - Select scopes: `bot`, `applications.commands`.
   - Select bot permissions: `Administrator` (or appropriate permissions: Manage Guild, Manage Roles, Manage Channels, Kick Members, Ban Members, Send Messages, Embed Links, etc.).

---

## 🎮 Running the Application

### Modern CLI Runner (Recommended)

Run everything or specific components using `src/__main__.py`:

```bash
# Run both Discord Bot and Web Dashboard concurrently:
python -m src --mode all

# Run only the Discord Bot:
python -m src --mode bot

# Run only the Web Dashboard:
python -m src --mode web

# Initialize or verify database tables:
python -m src --mode init-db
```

### Dedicated Scripts
```bash
# Start bot directly:
python scripts/run_bot.py

# Start dashboard directly:
python scripts/run_dashboard.py
```

### Legacy Entrypoints
For backwards compatibility with existing hosting setups:
```bash
python main.py        # Starts the bot
python webserver.py   # Starts the dashboard
```

---

## 🧪 Running Automated Tests

The test suite runs against an isolated in-memory SQLite database using `pytest`:

```bash
pytest -v
```

All database operations, business simulation workflows, counting games, formatting utilities, and dashboard routes are covered by automated unit tests.

---

## 📁 Project Structure

```
inv1s1bl3-bot/
├── .github/                  # GitHub Actions CI workflow & issue templates
│   ├── workflows/ci.yml
│   └── ISSUE_TEMPLATE/
├── alembic/                  # Database schema migrations
│   ├── versions/             # Migration scripts
│   └── env.py
├── assets/                   # Static application data & image assets
│   ├── data/                 # Game/market JSON catalogs
│   └── images/
├── docs/                     # Technical documentation
│   ├── architecture.md       # Deep dive into bot & dashboard architecture
│   ├── database.md           # Schema models, relations & migrations
│   ├── dashboard.md          # Web dashboard & OAuth2 guide
│   └── development.md        # Contributor guide & conventions
├── scripts/                  # Standalone execution scripts
│   ├── run_bot.py
│   ├── run_dashboard.py
│   └── init_db.py
├── src/
│   ├── bot/                  # Discord Bot core
│   │   ├── bot.py            # Custom commands.Bot subclass
│   │   ├── cogs/             # Modular Discord feature extensions (10 cogs)
│   │   ├── games/            # Interactive game state managers (GAW, RPS)
│   │   └── utils/            # Embed generators, text formatters, checks, API clients
│   ├── config/               # Type-safe configuration settings dataclass
│   ├── database/             # Async database layer
│   │   ├── models.py         # SQLAlchemy 2.0 ORM models
│   │   ├── session.py        # Dialect-agnostic engine & session factory
│   │   └── crud/             # Async database operations
│   └── web/                  # Flask Web Dashboard
│       ├── app.py            # Flask factory & session config
│       ├── auth.py           # Discord OAuth2 handler & CSRF verification
│       ├── routes.py         # Web endpoints (dashboard, servers, settings)
│       ├── static/           # Discord dark-theme CSS & JS assets
│       └── templates/        # Jinja2 HTML templates
├── tests/                    # Pytest test suite
├── .env.example              # Template environment configuration
├── .gitignore
├── CHANGELOG.md              # Version changelog
├── CONTRIBUTING.md           # Contribution guidelines
├── LICENSE                   # MIT License
├── MIGRATION.md              # Py-Cord to discord.py 2.x migration notes
├── pyproject.toml            # Project metadata & tool config
├── requirements.txt          # Python dependencies
└── SECURITY.md               # Security policy & credential rotation guidelines
```

---

## 🔒 Security & Credential Hygiene

- **No Hardcoded Secrets**: All tokens, client secrets, API keys, and connection strings are strictly loaded from environment variables via `src/config/settings.py`.
- **Private Data Sanitization**: This repository has undergone a strict security audit to ensure no private paths, email addresses, or old keys remain.
- **Rotating Leaked Legacy Keys**: If you obtained any legacy tokens from previous 2022 drafts, refer to [SECURITY.md](SECURITY.md) for immediate rotation procedures.

---

## 🤝 Contributing & Migrations

Contributions, bug reports, and suggestions are welcome!
- Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.
- If you are updating from an earlier 2022 Py-Cord version of this bot, please consult [MIGRATION.md](MIGRATION.md) for detailed database and architecture migration instructions.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.
