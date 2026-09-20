# Migration Guide: v1.0 (Legacy) to v2.0 (Modernized)

This guide documents the technical evolution of the **Inv1s1bl3 Bot** codebase from its original prototype built ~4 years ago as a student learning project to the modernized, production-ready open-source architecture.

---

## 1. Summary of Major Transitions

| Category | Legacy Architecture (v1.x) | Modernized Architecture (v2.x) |
| :--- | :--- | :--- |
| **Discord Library** | Py-Cord (`py-cord`) | Modern `discord.py 2.x` |
| **Command Pattern** | Prefix-only (`i.command`) & broken slash stubs | Hybrid commands (`@commands.hybrid_command`) & native app commands |
| **Database Access** | Scattered raw PostgreSQL `asyncpg` queries | Unified **SQLAlchemy 2.0 Async** ORM with CRUD repository pattern |
| **Supported Databases**| PostgreSQL only (hardcoded Azure credentials) | **SQLite (local/dev), PostgreSQL, MySQL/MariaDB** |
| **Migrations** | None (manual table execution scripts) | **Alembic** async migration engine |
| **Configuration** | Hardcoded secrets, tokens, and credentials | Type-safe environment variable parsing (`Settings`) & `.env.example` |
| **Web Dashboard** | Basic Flask with static CSS & unfinished stubs | Responsive Discord dark-theme UI with server management |
| **OAuth2 Security** | No CSRF verification (`state` parameter omitted) | Cryptographic CSRF state validation & secure session cookies |
| **Concurreny / I/O** | Synchronous `requests.get()` inside async cogs | Non-blocking async HTTP via `aiohttp.ClientSession` |
| **Testing** | Zero automated tests | Comprehensive `pytest` test suite across SQLite in-memory |

---

## 2. Discord Library & Cog Modernization

### Extension Setup
- **Before**: Synchronous `def setup(bot): bot.add_cog(Cog(bot))`
- **After**: Asynchronous `async def setup(bot: commands.Bot): await bot.add_cog(Cog(bot))`

### Slash & Hybrid Commands
Commands that benefit from Discord's autocomplete and slash command interface now use `@commands.hybrid_command()`. These commands function identically whether typed with the server prefix (e.g. `i.ping`) or executed via Discord's slash command selector (`/ping`).

### Moderation Upgrades
- `timeout`: Replaced manual `asyncio.sleep()` role removal with Discord's native member communication disabled API: `await member.timeout(timedelta(minutes=minutes))`.
- `bans`: Replaced deprecated discord.py 1.x `.flatten()` with modern async iterator syntax: `async for ban in ctx.guild.bans(): ...`.

---

## 3. Database Layer Migration

### PostgreSQL Array Columns Normalized
In the original implementation, user bag contents were stored as raw PostgreSQL array types:
```sql
-- Legacy raw SQL:
CREATE TABLE market (
    user_id BIGINT NOT NULL,
    bag TEXT[] NOT NULL,
    pieces INT[] NOT NULL
);
```
This prohibited running the bot on SQLite or MySQL. The schema is now normalized into a cross-database relational table:
```python
# Modern SQLAlchemy model:
class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="General")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
```

---

## 4. Upgrading Existing Installations

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up `.env`**:
   Copy `.env.example` to `.env` and fill in your Discord Bot Token and Client Secret.
3. **Run Schema Setup**:
   ```bash
   python -m src --mode init-db
   ```
   Or run Alembic migrations:
   ```bash
   alembic upgrade head
   ```
4. **Launch Bot & Dashboard**:
   ```bash
   python -m src --mode all
   ```
