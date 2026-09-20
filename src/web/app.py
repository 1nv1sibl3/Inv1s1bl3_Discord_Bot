from pathlib import Path
from flask import Flask, render_template

from src.config.settings import settings
from src.web.routes import auth_bp, main_bp


def create_app() -> Flask:
    web_dir = Path(__file__).resolve().parent
    template_dir = web_dir / "templates"
    static_dir = web_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    app.secret_key = settings.secret_key
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.is_production,
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # 2MB max request payload
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_global_vars():
        client_id = settings.discord_client_id
        invite_url = (
            f"https://discord.com/oauth2/authorize?client_id={client_id}"
            f"&permissions=8&scope=bot%20applications.commands"
        )
        return {
            "app_version": "2.0.0",
            "bot_client_id": client_id,
            "bot_invite_url": invite_url,
            "support_server_url": settings.support_server_url,
            "default_prefix": settings.default_prefix,
            "is_dev": settings.is_development,
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app
