"""
Legacy webserver compatibility wrapper.
Delegates to modern src.web dashboard application.
"""
from src.web.app import create_app

app = create_app()

if __name__ == "__main__":
    from src.config.settings import settings
    app.run(host=settings.dashboard_host, port=settings.dashboard_port)