from flask import Flask
from utils.response import success_response, error_response


def test_success_response():
    app = Flask(__name__)

    with app.app_context():
        response, status_code = success_response(
            message="OK",
            data={"result": "clean"},
            status_code=200
        )

        body = response.get_json()

        assert status_code == 200
        assert body["success"] is True
        assert body["message"] == "OK"
        assert body["data"]["result"] == "clean"


def test_error_response():
    app = Flask(__name__)

    with app.app_context():
        response, status_code = error_response(
            message="Bad request",
            errors={"url": "Invalid URL"},
            status_code=400
        )

        body = response.get_json()

        assert status_code == 400
        assert body["success"] is False
        assert body["message"] == "Bad request"
        assert body["errors"]["url"] == "Invalid URL"