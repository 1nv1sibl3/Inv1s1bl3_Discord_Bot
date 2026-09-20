"""
Legacy utils compatibility wrapper.
Delegates to modern src.bot.utils.
"""
from src.bot.utils import (
    text_to_owo,
    is_mod_or_owner,
    branded_embed,
    success_embed,
    error_embed,
    info_embed,
    warning_embed,
)

__all__ = [
    "text_to_owo",
    "is_mod_or_owner",
    "branded_embed",
    "success_embed",
    "error_embed",
    "info_embed",
    "warning_embed",
]
