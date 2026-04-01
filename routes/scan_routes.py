import time
import requests
from flask import Blueprint, request, jsonify
from services.scan_service import scan_url, scan_file

scan_bp = Blueprint('scan', __name__, url_prefix='/api/scan')



@scan_bp.route('/url', methods=['POST'])
def scan_url_route():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "Vui lòng nhập URL!"}), 400

    start_time = time.time()

    # 1. Quét URL bằng VirusTotal
    result = scan_url(url, user_id=None)



    return jsonify(result)


@scan_bp.route('/file', methods=['POST'])
def scan_file_route():
    if 'file' not in request.files:
        return jsonify({"error": "Không tìm thấy file!"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Bạn chưa chọn file!"}), 400

    start_time = time.time()

    # Quét file bằng VirusTotal
    result = scan_file(file, user_id=None)
    result["time"] = round(time.time() - start_time, 2)

    return jsonify(result)