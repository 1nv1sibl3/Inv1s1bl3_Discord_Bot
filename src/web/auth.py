import functools
import secrets
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from flask import flash, redirect, request, session, url_for
import requests

from src.config.settings import settings

DISCORD_API_BASE = "https://discord.com/api/v10"
MANAGE_GUILD_PERM = 0x00000020
ADMINISTRATOR_PERM = 0x00000008


def can_manage_guild(permissions: int) -> bool:
    """Check if permissions bitmask grants administrator or manage guild."""
    return bool(permissions & (ADMINISTRATOR_PERM | MANAGE_GUILD_PERM))


def get_oauth_login_url() -> str:
    """Generate Discord OAuth2 authorization URL with CSRF state token."""
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    client_id = settings.discord_client_id
    redirect_uri = quote(settings.discord_redirect_uri, safe="")
    scope = quote("identify guilds", safe="")

    return (
        f"https://discord.com/oauth2/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"state={state}&"
        f"prompt=consent"
    )


def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for OAuth2 access token."""
    data = {
        "client_id": settings.discord_client_id,
        "client_secret": settings.discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.discord_redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            f"{DISCORD_API_BASE}/oauth2/token",
            data=data,
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def fetch_user_data(access_token: str) -> Optional[Dict[str, Any]]:
    """Fetch Discord authenticated user profile."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"{DISCORD_API_BASE}/users/@me",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def fetch_user_guilds(access_token: str) -> List[Dict[str, Any]]:
    """Fetch list of guilds the user belongs to."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"{DISCORD_API_BASE}/users/@me/guilds",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session or "access_token" not in session:
            flash("Please log in with Discord to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
