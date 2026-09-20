import random
from typing import List

_VOWELS = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
_SMILEYS = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω´・)', '(´・ω・`)']


def text_to_owo(text: str) -> str:
    """Convert text into OwO speak."""
    if not text:
        return "UwU"

    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')

    for v in _VOWELS:
        if f'n{v}' in text:
            text = text.replace(f'n{v}', f'ny{v}')
        if f'N{v}' in text:
            text = text.replace(f'N{v}', f'N{"Y" if v.isupper() else "y"}{v}')

    # Replace punctuation with random smileys
    if '!' in text:
        parts = text.rsplit('!', 1)
        text = f" {random.choice(_SMILEYS)}".join(parts)
    if '?' in text:
        parts = text.rsplit('?', 1)
        text = " owo".join(parts)
    if '.' in text:
        parts = text.rsplit('.', 1)
        text = f" {random.choice(_SMILEYS)}".join(parts)

    return text


def create_progress_bar(current: int, total: int, length: int = 15) -> str:
    """Return an emoji progress bar."""
    if total <= 0:
        total = 1
    pct = max(0.0, min(1.0, current / total))
    filled = int(round(pct * length))
    unfilled = length - filled
    return f"{'🟦' * filled}{'⬜' * unfilled} `{int(pct * 100)}%`"


def format_timespan(seconds: int) -> str:
    """Format seconds into human-readable string like '2d 4h 30m 15s'."""
    if seconds <= 0:
        return "0s"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts: List[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_currency(amount: int) -> str:
    """Format integer amount as localized currency string."""
    return f"{amount:,} iC"
