import time
import requests
from flask import Blueprint, request, jsonify, session
from services.scan_service import scan_url, scan_file
from utils.scan_formatter import format_file_result  
scan_bp = Blueprint('scan', __name__, url_prefix='/api/scan')

@scan_bp.route('/url', methods=['POST'])
def scan_url_route():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "Vui lòng nhập URL!"}), 400
    user_id = session.get('user_id')  # Lấy từ session
    start_time = time.time()
    result = scan_url(url, user_id=user_id)
    result["time"] = round(time.time() - start_time, 2)

    return jsonify(result)

@scan_bp.route('/file', methods=['POST'])
def scan_file_route():
    if 'file' not in request.files:
        return jsonify({"error": "Không tìm thấy file!"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Bạn chưa chọn file!"}), 400

    start_time = time.time()
    user_id = session.get('user_id')  # Lấy từ session
    clean_result = scan_file(file, user_id=user_id)
    result = format_file_result(clean_result)  # dùng formatter cho file
    result["time"] = round(time.time() - start_time, 2)
    return jsonify(result)