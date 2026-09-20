import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import crud


@pytest.mark.asyncio
async def test_server_settings_lifecycle(db_session: AsyncSession):
    guild_id = 123456789

    # Default prefix
    prefix = await crud.server.get_prefix(db_session, guild_id)
    assert prefix == "i."

    # Update prefix
    ok = await crud.server.set_prefix(db_session, guild_id, "!")
    assert ok is True
    updated_prefix = await crud.server.get_prefix(db_session, guild_id)
    assert updated_prefix == "!"

    # Update welcome settings
    s = await crud.server.update_welcome_settings(
        db_session, guild_id, enabled=True, channel_id=55555, message="Hello {user}!"
    )
    assert s.welcome_enabled is True
    assert s.welcome_channel_id == 55555
    assert s.welcome_message == "Hello {user}!"


@pytest.mark.asyncio
async def test_countgame_mechanics(db_session: AsyncSession):
    guild_id = 987654
    channel_id = 112233

    # Configure channel
    game = await crud.countgame.set_count_channel(db_session, guild_id, channel_id)
    assert game.current_count == 0

    # User 1 counts 1 (correct)
    ok, count, reason = await crud.countgame.process_count(
        db_session, guild_id, channel_id, user_id=101, number=1
    )
    assert ok is True
    assert count == 1
    assert reason == "correct"

    # User 1 tries to count 2 consecutively (anti-solo counting violation)
    ok2, count2, reason2 = await crud.countgame.process_count(
        db_session, guild_id, channel_id, user_id=101, number=2
    )
    assert ok2 is False
    assert reason2 == "consecutive"

    # User 2 counts 1 to restart
    ok3, count3, _ = await crud.countgame.process_count(
        db_session, guild_id, channel_id, user_id=102, number=1
    )
    assert ok3 is True
    assert count3 == 1

    # User 1 counts wrong number (e.g. 5 instead of 2)
    ok4, _, reason4 = await crud.countgame.process_count(
        db_session, guild_id, channel_id, user_id=101, number=5
    )
    assert ok4 is False
    assert reason4 == "wrong_number"
