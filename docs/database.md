# Inv1s1bl3 Bot — Database Architecture & Migrations

## 1. Supported Database Backends

Inv1s1bl3 Bot supports three major database engines out of the box via SQLAlchemy 2.0 Async:

| Engine | Connection Scheme | Driver | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **SQLite** | `sqlite+aiosqlite:///data/bot.db` | `aiosqlite` | Local development, testing, zero-configuration |
| **PostgreSQL** | `postgresql+asyncpg://user:pass@host:5432/dbname` | `asyncpg` | Production high-concurrency deployments |
| **MySQL / MariaDB** | `mysql+aiomysql://user:pass@host:3306/dbname` | `aiomysql` | Production LAMP/LEMP environments |

---

## 2. Entity Relational Models

```
+-------------------------------------------------------------+
|                         user_levels                         |
+-------------------------------------------------------------+
| id          | Integer (PK, Autoincrement)                   |
| user_id     | BigInteger (Discord User Snowflake, Indexed)  |
| guild_id    | BigInteger (Guild ID or 0 for global)         |
| xp          | BigInteger (Total accumulated experience)     |
| level       | BigInteger (Computed level)                   |
+-------------+-----------------------------------------------+
  UNIQUE(user_id, guild_id)

+-------------------------------------------------------------+
|                       economy_accounts                      |
+-------------------------------------------------------------+
| user_id     | BigInteger (PK, Discord User Snowflake)       |
| wallet      | BigInteger (Liquid wallet balance)            |
| bank        | BigInteger (Protected bank vault balance)     |
| last_daily  | DateTime (UTC timestamp of last daily reward) |
+-------------+-----------------------------------------------+

+-------------------------------------------------------------+
|                       inventory_items                       |
+-------------------------------------------------------------+
| id          | Integer (PK, Autoincrement)                   |
| user_id     | BigInteger (Discord User Snowflake, Indexed)  |
| item_id     | String(64) (e.g. 'smart-watch', 'laptop')     |
| item_name   | String(128) (Display name)                    |
| category    | String(64) (e.g. 'IoT', 'Veg', 'Vehicles')    |
| quantity    | Integer (Amount owned)                        |
+-------------+-----------------------------------------------+
  UNIQUE(user_id, item_id)

+-------------------------------------------------------------+
|                        guild_settings                       |
+-------------------------------------------------------------+
| id                 | Integer (PK, Autoincrement)            |
| guild_id           | BigInteger (Unique, Indexed)           |
| prefix             | String(10) (Default: 'i.')             |
| welcome_enabled    | Boolean (Default: False)               |
| welcome_channel_id | BigInteger (Nullable)                  |
| welcome_message    | Text (Nullable)                        |
| leave_enabled      | Boolean (Default: False)               |
| leave_channel_id   | BigInteger (Nullable)                  |
| leave_message      | Text (Nullable)                        |
| mod_role_id        | BigInteger (Nullable)                  |
| mute_role_id       | BigInteger (Nullable)                  |
| mod_log_channel_id | BigInteger (Nullable)                  |
+--------------------+----------------------------------------+

+-------------------------------------------------------------+
|                          businesses                         |
+-------------------------------------------------------------+
| id            | Integer (PK, Autoincrement)                 |
| owner_id      | BigInteger (Unique, Indexed, Owner ID)      |
| name          | String(64) (Unique Company Name)            |
| balance       | BigInteger (Treasury balance)               |
| company_value | BigInteger (Total business valuation)       |
| created_at    | DateTime (UTC creation timestamp)           |
+---------------+---------------------------------------------+
       | 1
       |
       | N
+-------------------------------------------------------------+
|                           products                          |
+-------------------------------------------------------------+
| id                       | Integer (PK, Autoincrement)      |
| business_id              | Integer (FK -> businesses.id)    |
| name                     | String(64) (Product Name)        |
| price                    | Integer (Selling price)          |
| level                    | Integer (Product level)          |
| num_manufactured         | Integer (Units in stock)         |
| num_employees            | Integer (Assigned workforce)     |
| time_to_make_one_product | Integer (Seconds per cycle)      |
| last_sold_timestamp      | DateTime (Last cycle timestamp)  |
| total_sold               | Integer (Cumulative units sold)  |
+--------------------------+----------------------------------+
  UNIQUE(business_id, name)
```

---

## 3. Database Migrations with Alembic

Alembic is pre-configured to inspect the `Base.metadata` models and manage migrations across all database backends.

### Apply Migrations
```bash
alembic upgrade head
```

### Generate a New Migration
```bash
alembic revision --autogenerate -m "describe_changes"
```

### Rollback Previous Migration
```bash
alembic downgrade -1
```
