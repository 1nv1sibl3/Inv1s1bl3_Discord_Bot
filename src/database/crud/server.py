from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import GuildSettings


async def get_or_create_guild_settings(
    session: AsyncSession, guild_id: int, default_prefix: str = "i."
) -> GuildSettings:
    stmt = select(GuildSettings).where(GuildSettings.guild_id == guild_id)
    result = await session.execute(stmt)
    settings_obj = result.scalar_one_or_none()
    if settings_obj is None:
        settings_obj = GuildSettings(
            guild_id=guild_id,
            prefix=default_prefix,
            welcome_enabled=False,
            leave_enabled=False,
        )
        session.add(settings_obj)
        await session.flush()
    return settings_obj


async def get_prefix(
    session: AsyncSession, guild_id: int, default_prefix: str = "i."
) -> str:
    stmt = select(GuildSettings.prefix).where(GuildSettings.guild_id == guild_id)
    result = await session.execute(stmt)
    prefix = result.scalar_one_or_none()
    return prefix if prefix else default_prefix


async def set_prefix(
    session: AsyncSession, guild_id: int, prefix: str
) -> bool:
    prefix = prefix.strip()
    if not prefix or len(prefix) > 10:
        return False
    settings_obj = await get_or_create_guild_settings(session, guild_id)
    settings_obj.prefix = prefix
    await session.commit()
    return True


async def update_welcome_settings(
    session: AsyncSession,
    guild_id: int,
    enabled: bool,
    channel_id: Optional[int] = None,
    message: Optional[str] = None,
) -> GuildSettings:
    settings_obj = await get_or_create_guild_settings(session, guild_id)
    settings_obj.welcome_enabled = enabled
    if channel_id is not None:
        settings_obj.welcome_channel_id = channel_id
    if message is not None:
        settings_obj.welcome_message = message
    await session.commit()
    return settings_obj


async def update_leave_settings(
    session: AsyncSession,
    guild_id: int,
    enabled: bool,
    channel_id: Optional[int] = None,
    message: Optional[str] = None,
) -> GuildSettings:
    settings_obj = await get_or_create_guild_settings(session, guild_id)
    settings_obj.leave_enabled = enabled
    if channel_id is not None:
        settings_obj.leave_channel_id = channel_id
    if message is not None:
        settings_obj.leave_message = message
    await session.commit()
    return settings_obj


async def update_mod_settings(
    session: AsyncSession,
    guild_id: int,
    mod_role_id: Optional[int] = None,
    mute_role_id: Optional[int] = None,
    mod_log_channel_id: Optional[int] = None,
) -> GuildSettings:
    settings_obj = await get_or_create_guild_settings(session, guild_id)
    if mod_role_id is not None:
        settings_obj.mod_role_id = mod_role_id
    if mute_role_id is not None:
        settings_obj.mute_role_id = mute_role_id
    if mod_log_channel_id is not None:
        settings_obj.mod_log_channel_id = mod_log_channel_id
    await session.commit()
    return settings_obj
