from src.web.app import create_app


def test_dashboard_routes():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # Index page
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Inv1s1bl3" in resp.data

    # Protected dashboard redirects to login when unauthenticated
    resp_dash = client.get("/dashboard")
    assert resp_dash.status_code == 302
    assert "/login" in resp_dash.headers["Location"]

    # Protected servers redirects to login
    resp_serv = client.get("/servers")
    assert resp_serv.status_code == 302

    # 404 handler
    resp_404 = client.get("/does-not-exist")
    assert resp_404.status_code == 404
    assert b"404" in resp_404.data
