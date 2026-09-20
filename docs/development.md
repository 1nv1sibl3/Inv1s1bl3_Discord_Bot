# Inv1s1bl3 Bot — Developer Guide

## 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- Discord Developer Application & Bot Token

---

## 2. Local Setup Instructions

### Clone & Navigate
```bash
git clone https://github.com/yourusername/inv1s1bl3-bot.git
cd inv1s1bl3-bot
```

### Create Virtual Environment
```bash
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio ruff
```

### Configure Environment Variables
Copy the template and edit your credentials:
```bash
cp .env.example .env
```

At minimum, set:
- `DISCORD_TOKEN=your_actual_bot_token`
- `DATABASE_URL=sqlite+aiosqlite:///data/bot.db`

---

## 3. Running the Project

### Initialize Database Tables
```bash
python -m src --mode init-db
```

### Start Discord Bot Only
```bash
python -m src --mode bot
```

### Start Web Dashboard Only
```bash
python -m src --mode web
```

### Start Both (Bot + Dashboard)
```bash
python -m src --mode all
```

---

## 4. Running Automated Tests

Run the complete pytest test suite:
```bash
pytest -v
```

Run specific test modules:
```bash
pytest tests/test_economy_crud.py
pytest tests/test_business_crud.py
pytest tests/test_dashboard.py
```

---

## 5. Code Formatting & Linting

```bash
# Check code style with ruff
ruff check src tests

# Format code
ruff format src tests
```
