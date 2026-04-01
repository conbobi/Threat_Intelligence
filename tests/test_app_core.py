def test_app_created(app):
    assert app is not None
    assert app.config["TESTING"] is True


def test_upload_folder_config(app):
    assert app.config["UPLOAD_FOLDER"] == "temp_uploads"


def test_health_route_exists(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_blueprints_registered(app):
    assert "auth" in app.blueprints
    assert "user" in app.blueprints
    assert "scan" in app.blueprints
    assert "admin" in app.blueprints