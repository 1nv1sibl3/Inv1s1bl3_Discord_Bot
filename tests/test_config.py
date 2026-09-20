import pytest
from src.config.settings import Settings


def test_default_settings():
    s = Settings(
        environment="development",
        discord_token="fake_token",
        default_prefix="i.",
    )
    assert s.is_development is True
    assert s.is_production is False
    assert s.default_prefix == "i."
    assert s.database_url is not None


def test_bot_config_validation():
    s_invalid = Settings(discord_token="")
    with pytest.raises(ValueError, match="DISCORD_TOKEN is missing"):
        s_invalid.validate_bot_config()

    s_valid = Settings(discord_token="valid_discord_token_string")
    s_valid.validate_bot_config()  # Should not raise


def test_dashboard_config_validation():
    s_invalid = Settings(discord_client_id=0)
    with pytest.raises(ValueError, match="DISCORD_CLIENT_ID is required"):
        s_invalid.validate_dashboard_config()
