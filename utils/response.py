from flask import jsonify

def success_response(message="Success", data=None, status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data or {}
    }), status_code

def error_response(message="Error", errors=None, status_code=400):
    return jsonify({
        "success": False,
        "message": message,
        "errors": errors or {}
    }), status_code