import time
import requests
from flask import Blueprint, request, jsonify
from services.scan_service import scan_url, scan_file

scan_bp = Blueprint('scan', __name__, url_prefix='/api/scan')


def analyze_website_html(url):
    """
    Phân tích HTML cơ bản của website bằng BeautifulSoup
    """
    try:
        response = requests.get(url, timeout=8, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "Không có tiêu đề"

        html_info = {
            "title": title,
            "num_links": len(soup.find_all("a")),
            "num_forms": len(soup.find_all("form")),
            "num_iframes": len(soup.find_all("iframe")),
            "num_scripts": len(soup.find_all("script")),
        }

        # Lấy thử một số link đầu tiên để tham khảo
        links = []
        for a in soup.find_all("a", href=True)[:5]:
            links.append(a["href"])

        html_info["sample_links"] = links

        return html_info

    except Exception as e:
        return {
            "error": f"Không thể phân tích HTML website: {str(e)}"
        }


@scan_bp.route('/url', methods=['POST'])
def scan_url_route():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "Vui lòng nhập URL!"}), 400

    start_time = time.time()

    # 1. Quét URL bằng VirusTotal
    result = scan_url(url, user_id=None)

    # 2. Phân tích HTML bằng BeautifulSoup
    html_analysis = analyze_website_html(url)

    # 3. Gộp kết quả
    result["html_analysis"] = html_analysis
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

    # Quét file bằng VirusTotal
    result = scan_file(file, user_id=None)
    result["time"] = round(time.time() - start_time, 2)

    return jsonify(result)