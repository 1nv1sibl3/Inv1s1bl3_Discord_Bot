from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import UserLevel


async def get_or_create_user_level(
    session: AsyncSession, user_id: int, guild_id: int = 0
) -> UserLevel:
    stmt = select(UserLevel).where(
        UserLevel.user_id == user_id, UserLevel.guild_id == guild_id
    )
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    if record is None:
        record = UserLevel(user_id=user_id, guild_id=guild_id, xp=5, level=0)
        session.add(record)
        await session.flush()
    return record


async def increase_xp(
    session: AsyncSession, user_id: int, guild_id: int, rate: int = 10
) -> Tuple[UserLevel, bool, int]:
    """
    Increment XP for a user in a guild.
    Returns: (record, leveled_up, new_level)
    """
    record = await get_or_create_user_level(session, user_id, guild_id)
    record.xp += rate
    old_level = record.level
    calculated_level = int(record.xp ** 0.25)

    leveled_up = calculated_level > old_level
    if leveled_up:
        record.level = calculated_level

    await session.commit()
    return record, leveled_up, record.level


async def get_user_data(
    session: AsyncSession, user_id: int, guild_id: int
) -> dict:
    record = await get_or_create_user_level(session, user_id, guild_id)
    return {
        "user_id": record.user_id,
        "guild_id": record.guild_id,
        "xp": record.xp,
        "level": record.level,
    }


async def get_rank(session: AsyncSession, user_id: int, guild_id: int) -> int:
    """Return 1-indexed rank of user in the guild based on XP."""
    await get_or_create_user_level(session, user_id, guild_id)
    stmt = (
        select(UserLevel.user_id)
        .where(UserLevel.guild_id == guild_id)
        .order_by(desc(UserLevel.xp))
    )
    result = await session.execute(stmt)
    user_ids = result.scalars().all()
    try:
        return user_ids.index(user_id) + 1
    except ValueError:
        return len(user_ids)


async def get_server_leaderboard(
    session: AsyncSession, guild_id: int, limit: int = 10
) -> List[UserLevel]:
    stmt = (
        select(UserLevel)
        .where(UserLevel.guild_id == guild_id)
        .order_by(desc(UserLevel.xp))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_global_ranking(session: AsyncSession, user_id: int) -> int:
    """Calculate global ranking based on aggregate XP across all guilds."""
    stmt = (
        select(UserLevel.user_id, func.sum(UserLevel.xp).label("total_xp"))
        .group_by(UserLevel.user_id)
        .order_by(desc("total_xp"))
    )
    result = await session.execute(stmt)
    rows = result.all()
    for index, (uid, _) in enumerate(rows):
        if uid == user_id:
            return index + 1
    return len(rows) + 1


async def get_global_leaderboard(
    session: AsyncSession, limit: int = 10
) -> List[Tuple[int, int]]:
    """Return top users globally: list of (user_id, total_xp)."""
    stmt = (
        select(UserLevel.user_id, func.sum(UserLevel.xp).label("total_xp"))
        .group_by(UserLevel.user_id)
        .order_by(desc("total_xp"))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [(row[0], int(row[1])) for row in result.all()]
