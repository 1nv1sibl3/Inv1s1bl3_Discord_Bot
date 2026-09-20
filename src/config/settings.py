import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from project root if present
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _ROOT_DIR / ".env"
if _ENV_FILE.exists():
    load_dotenv(dotenv_path=_ENV_FILE)
else:
    load_dotenv()


def _get_list_of_ints(env_var: str, default: str = "") -> List[int]:
    val = os.getenv(env_var, default).strip()
    if not val:
        return []
    result = []
    for item in val.split(","):
        item = item.strip()
        if item.isdigit():
            result.append(int(item))
    return result


@dataclass(frozen=True)
class Settings:
    # Application Environment
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Discord Bot Configuration
    discord_token: str = os.getenv("DISCORD_TOKEN", "")
    default_prefix: str = os.getenv("DEFAULT_PREFIX", "i.")
    support_server_url: str = os.getenv("SUPPORT_SERVER_URL", "https://discord.gg/UQ6Uh4d4nM")
    owner_ids: List[int] = field(default_factory=lambda: _get_list_of_ints("OWNER_IDS"))

    # Discord OAuth2 & Client Details
    discord_client_id: int = int(os.getenv("DISCORD_CLIENT_ID", "0")) if os.getenv("DISCORD_CLIENT_ID", "0").isdigit() else 0
    discord_client_secret: str = os.getenv("DISCORD_CLIENT_SECRET", "")
    discord_redirect_uri: str = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8082/callback")

    # Database Configuration (SQLAlchemy 2.0 Async URL)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///data/bot.db"
    )

    # Web Dashboard Settings
    secret_key: str = os.getenv("SECRET_KEY", "insecure-dev-key-change-in-production")
    dashboard_host: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    dashboard_port: int = int(os.getenv("DASHBOARD_PORT", "8082")) if os.getenv("DASHBOARD_PORT", "8082").isdigit() else 8082
    dashboard_base_url: str = os.getenv("DASHBOARD_BASE_URL", "http://localhost:8082")

    # Optional External APIs
    nasa_api_key: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
    giphy_api_key: str = os.getenv("GIPHY_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate_bot_config(self) -> None:
        """Validate required configuration for bot execution."""
        if not self.discord_token or self.discord_token == "your_discord_bot_token_here":
            raise ValueError(
                "DISCORD_TOKEN is missing or not configured. "
                "Please set DISCORD_TOKEN in your environment or .env file."
            )

    def validate_dashboard_config(self) -> None:
        """Validate required configuration for web dashboard execution."""
        if not self.discord_client_id:
            raise ValueError("DISCORD_CLIENT_ID is required for the web dashboard.")
        if not self.discord_client_secret or self.discord_client_secret == "your_discord_client_secret_here":
            raise ValueError("DISCORD_CLIENT_SECRET is required for the web dashboard OAuth2.")
        if self.is_production and self.secret_key == "insecure-dev-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed from default in production.")


# Singleton settings instance
settings = Settings()
