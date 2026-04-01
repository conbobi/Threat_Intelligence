from flask import Flask, session
from utils.decorators import login_required, admin_required


def create_test_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True

    @app.route("/login", endpoint="auth.login")
    def fake_login():
        return "login page", 200

    @app.route("/admin/login", endpoint="admin.login")
    def fake_admin_login():
        return "admin login page", 200

    @app.route("/protected")
    @login_required
    def protected():
        return "protected ok", 200

    @app.route("/admin/protected")
    @admin_required
    def admin_protected():
        return "admin protected ok", 200

    return app


def test_login_required_redirects_when_not_logged_in():
    app = create_test_app()
    client = app.test_client()

    response = client.get("/protected")
    assert response.status_code in (301, 302)


def test_login_required_allows_logged_in_user():
    app = create_test_app()
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/protected")
    assert response.status_code == 200
    assert response.data.decode() == "protected ok"


def test_admin_required_redirects_when_not_admin():
    app = create_test_app()
    client = app.test_client()

    response = client.get("/admin/protected")
    assert response.status_code in (301, 302)


def test_admin_required_allows_admin():
    app = create_test_app()
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["is_admin"] = True

    response = client.get("/admin/protected")
    assert response.status_code == 200
    assert response.data.decode() == "admin protected ok"