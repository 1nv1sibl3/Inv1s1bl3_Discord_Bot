import argparse
import asyncio
import logging
import sys
import threading
from typing import Optional

from src.config.settings import settings
from src.database.session import init_db


def setup_logging(level_name: Optional[str] = None):
    level = getattr(logging, level_name or settings.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Suppress verbose third-party loggers unless debugging
    if level > logging.DEBUG:
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.INFO)


async def run_bot():
    from src.bot.bot import Inv1s1bl3Bot

    settings.validate_bot_config()
    bot = Inv1s1bl3Bot()
    logger = logging.getLogger("inv1s1bl3.main")
    logger.info("Starting Inv1s1bl3 Discord Bot...")
    try:
        await bot.start(settings.discord_token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Closing bot...")
        await bot.close()


def run_web():
    from src.web.app import create_app

    settings.validate_dashboard_config()
    logger = logging.getLogger("inv1s1bl3.web")
    logger.info(f"Starting Inv1s1bl3 Web Dashboard on {settings.dashboard_host}:{settings.dashboard_port}...")
    app = create_app()
    app.run(
        host=settings.dashboard_host,
        port=settings.dashboard_port,
        debug=settings.is_development,
        use_reloader=False,
    )


def run_all():
    """Run bot and dashboard together concurrently."""
    logger = logging.getLogger("inv1s1bl3.main")
    logger.info("Starting Inv1s1bl3 Bot and Web Dashboard concurrently...")

    web_thread = threading.Thread(target=run_web, daemon=True, name="DashboardThread")
    web_thread.start()

    asyncio.run(run_bot())


def main():
    parser = argparse.ArgumentParser(
        description="Inv1s1bl3 Bot - Revived & Modernized Open-Source Discord Suite"
    )
    parser.add_argument(
        "--mode",
        choices=["bot", "web", "all", "init-db"],
        default="bot",
        help="Execution mode: 'bot' (Discord bot only), 'web' (dashboard only), 'all' (both), or 'init-db' (create tables)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Override default logging verbosity level",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)

    if args.mode == "init-db":
        logging.info("Initializing database schema...")
        asyncio.run(init_db())
        logging.info("Database schema initialized successfully.")
    elif args.mode == "web":
        run_web()
    elif args.mode == "all":
        run_all()
    else:
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
