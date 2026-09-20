import asyncio
import concurrent.futures
import logging
from typing import Any, Coroutine, Dict, List

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.config.settings import settings
from src.database.session import get_db_session
from src.database import crud
from src.web.auth import (
    can_manage_guild,
    exchange_code_for_token,
    fetch_user_data,
    fetch_user_guilds,
    get_oauth_login_url,
    login_required,
)

logger = logging.getLogger("inv1s1bl3.web")

auth_bp = Blueprint("auth", __name__)
main_bp = Blueprint("main", __name__)


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an async coroutine safely from synchronous Flask context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return loop.run_until_complete(coro)


# ------------------------------------------------------------------------------
# Authentication Routes
# ------------------------------------------------------------------------------

@auth_bp.route("/login")
def login():
    if "user" in session and "access_token" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(get_oauth_login_url())


@auth_bp.route("/callback")
def callback():
    state = request.args.get("state")
    expected_state = session.pop("oauth_state", None)

    if not state or state != expected_state:
        flash("Authentication failed: State parameter mismatch or expired. Please try again.", "error")
        return redirect(url_for("main.index"))

    code = request.args.get("code")
    if not code:
        error_desc = request.args.get("error_description", "Authorization was denied.")
        flash(f"Login failed: {error_desc}", "error")
        return redirect(url_for("main.index"))

    token_data = exchange_code_for_token(code)
    if not token_data or "access_token" not in token_data:
        flash("Failed to retrieve access token from Discord.", "error")
        return redirect(url_for("main.index"))

    access_token = token_data["access_token"]
    user_info = fetch_user_data(access_token)
    if not user_info:
        flash("Failed to retrieve user profile from Discord.", "error")
        return redirect(url_for("main.index"))

    # Populate session
    session["access_token"] = access_token
    session["user"] = {
        "id": user_info["id"],
        "username": user_info["username"],
        "discriminator": user_info.get("discriminator", "0"),
        "global_name": user_info.get("global_name") or user_info["username"],
        "avatar": user_info.get("avatar"),
    }

    flash(f"Welcome back, {session['user']['global_name']}!", "success")
    return redirect(url_for("main.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))


# ------------------------------------------------------------------------------
# Main Dashboard & Server Management Routes
# ------------------------------------------------------------------------------

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    token = session["access_token"]
    guilds = fetch_user_guilds(token)

    manageable_count = sum(1 for g in guilds if can_manage_guild(int(g.get("permissions", 0))))

    return render_template(
        "dashboard.html",
        user=user,
        total_guilds=len(guilds),
        manageable_count=manageable_count,
    )


@main_bp.route("/servers")
@login_required
def servers():
    token = session["access_token"]
    user_guilds = fetch_user_guilds(token)

    # In a web dashboard, we can check mutual servers if the bot client ID is known
    client_id = settings.discord_client_id

    manageable_servers = []
    other_servers = []

    for g in user_guilds:
        perms = int(g.get("permissions", 0))
        can_manage = can_manage_guild(perms)
        server_info = {
            "id": g["id"],
            "name": g["name"],
            "icon": g.get("icon"),
            "can_manage": can_manage,
            "invite_url": (
                f"https://discord.com/oauth2/authorize?client_id={client_id}"
                f"&permissions=8&scope=bot%20applications.commands&guild_id={g['id']}"
            ),
        }
        if can_manage:
            manageable_servers.append(server_info)
        else:
            other_servers.append(server_info)

    return render_template(
        "servers.html",
        manageable_servers=manageable_servers,
        other_servers=other_servers,
    )


@main_bp.route("/servers/<int:guild_id>", methods=["GET", "POST"])
@login_required
def guild_manage(guild_id: int):
    token = session["access_token"]
    user_guilds = fetch_user_guilds(token)

    # Security check: User must be in this guild and have manage permissions!
    target_guild = None
    for g in user_guilds:
        if int(g["id"]) == guild_id:
            if can_manage_guild(int(g.get("permissions", 0))):
                target_guild = g
            break

    if not target_guild:
        flash("You do not have permission to manage this server.", "error")
        return redirect(url_for("main.servers"))

    async def get_settings():
        async with get_db_session() as db_sess:
            return await crud.server.get_or_create_guild_settings(db_sess, guild_id, settings.default_prefix)

    guild_cfg = run_async(get_settings())

    if request.method == "POST":
        new_prefix = request.form.get("prefix", "i.").strip()
        welcome_enabled = request.form.get("welcome_enabled") == "on"
        welcome_channel_raw = request.form.get("welcome_channel_id", "").strip()
        welcome_channel = int(welcome_channel_raw) if welcome_channel_raw.isdigit() else None
        welcome_message = request.form.get("welcome_message", "").strip() or None

        leave_enabled = request.form.get("leave_enabled") == "on"
        leave_channel_raw = request.form.get("leave_channel_id", "").strip()
        leave_channel = int(leave_channel_raw) if leave_channel_raw.isdigit() else None
        leave_message = request.form.get("leave_message", "").strip() or None

        async def update_settings():
            async with get_db_session() as db_sess:
                await crud.server.set_prefix(db_sess, guild_id, new_prefix)
                await crud.server.update_welcome_settings(
                    db_sess, guild_id, welcome_enabled, welcome_channel, welcome_message
                )
                await crud.server.update_leave_settings(
                    db_sess, guild_id, leave_enabled, leave_channel, leave_message
                )

        run_async(update_settings())
        flash(f"Settings for {target_guild['name']} updated successfully!", "success")
        return redirect(url_for("main.guild_manage", guild_id=guild_id))

    return render_template(
        "guild_manage.html",
        guild=target_guild,
        cfg=guild_cfg,
    )


@main_bp.route("/profile")
@login_required
def profile():
    user = session["user"]
    token = session["access_token"]
    guilds = fetch_user_guilds(token)

    async def get_user_econ():
        async with get_db_session() as db_sess:
            return await crud.economy.get_balance(db_sess, int(user["id"]))

    balance = run_async(get_user_econ())

    return render_template(
        "profile.html",
        user=user,
        guilds=guilds,
        balance=balance,
    )
