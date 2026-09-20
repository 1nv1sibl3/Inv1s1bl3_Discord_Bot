from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import CountGame


async def get_count_game(
    session: AsyncSession, guild_id: int, channel_id: int
) -> Optional[CountGame]:
    stmt = select(CountGame).where(
        CountGame.guild_id == guild_id, CountGame.channel_id == channel_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def set_count_channel(
    session: AsyncSession, guild_id: int, channel_id: int
) -> CountGame:
    game = await get_count_game(session, guild_id, channel_id)
    if game is None:
        game = CountGame(
            guild_id=guild_id,
            channel_id=channel_id,
            current_count=0,
            last_user_id=None,
        )
        session.add(game)
    else:
        game.current_count = 0
        game.last_user_id = None
    await session.commit()
    return game


async def remove_count_channel(
    session: AsyncSession, guild_id: int, channel_id: int
) -> bool:
    game = await get_count_game(session, guild_id, channel_id)
    if game is None:
        return False
    await session.delete(game)
    await session.commit()
    return True


async def process_count(
    session: AsyncSession,
    guild_id: int,
    channel_id: int,
    user_id: int,
    number: int,
) -> Tuple[bool, int, str]:
    """
    Process a counting attempt.
    Returns: (success, current_count, reason)
    """
    game = await get_count_game(session, guild_id, channel_id)
    if game is None:
        return False, 0, "not_configured"

    # Anti-solo counting check: a user cannot count twice in a row
    if game.last_user_id == user_id and game.current_count > 0:
        old = game.current_count
        game.current_count = 0
        game.last_user_id = None
        await session.commit()
        return False, old, "consecutive"

    expected = game.current_count + 1
    if number != expected:
        old = game.current_count
        game.current_count = 0
        game.last_user_id = None
        await session.commit()
        return False, old, "wrong_number"

    game.current_count = expected
    game.last_user_id = user_id
    await session.commit()
    return True, expected, "correct"
