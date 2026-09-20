from datetime import datetime, timezone
from typing import Optional
import discord

# Inv1s1bl3 Bot Brand Colors
COLOR_BRAND = 0x5865F2    # Blurple
COLOR_SUCCESS = 0x57F287  # Green
COLOR_ERROR = 0xED4245    # Red
COLOR_WARNING = 0xFEE75C  # Yellow
COLOR_INFO = 0x5865F2     # Blurple
COLOR_DARK = 0x2B2D31     # Discord dark theme background


def branded_embed(
    title: str,
    description: Optional[str] = None,
    color: int = COLOR_BRAND,
    footer: Optional[str] = None,
    footer_icon: Optional[str] = None,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    timestamp: bool = True,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc) if timestamp else None,
    )
    if footer:
        embed.set_footer(text=footer, icon_url=footer_icon)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    return embed


def success_embed(
    title: str = "Success",
    description: Optional[str] = None,
    footer: Optional[str] = None,
) -> discord.Embed:
    return branded_embed(
        title=f"✅ {title}",
        description=description,
        color=COLOR_SUCCESS,
        footer=footer,
    )


def error_embed(
    title: str = "Error",
    description: Optional[str] = None,
    footer: Optional[str] = None,
) -> discord.Embed:
    return branded_embed(
        title=f"❌ {title}",
        description=description,
        color=COLOR_ERROR,
        footer=footer,
    )


def warning_embed(
    title: str = "Warning",
    description: Optional[str] = None,
    footer: Optional[str] = None,
) -> discord.Embed:
    return branded_embed(
        title=f"⚠️ {title}",
        description=description,
        color=COLOR_WARNING,
        footer=footer,
    )


def info_embed(
    title: str = "Information",
    description: Optional[str] = None,
    footer: Optional[str] = None,
) -> discord.Embed:
    return branded_embed(
        title=f"ℹ️ {title}",
        description=description,
        color=COLOR_INFO,
        footer=footer,
    )
