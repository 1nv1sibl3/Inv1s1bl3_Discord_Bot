"""
Legacy settings compatibility wrapper.
Delegates to modern src.config.settings.
"""
from src.config.settings import settings

DEBUG = settings.is_development
DEFAULT_PREFIX = settings.default_prefix
DISCORD_TOKEN = settings.discord_token
DATABASE_URL = settings.database_url
