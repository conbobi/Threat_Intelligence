import requests
import hashlib
import base64
from config import Config

VIRUSTOTAL_API_KEY = Config.VIRUSTOTAL_API_KEY


def scan_url_with_virustotal(target_url):
    if not VIRUSTOTAL_API_KEY:
        return {"error": "Chưa cấu hình API Key VirusTotal"}

    url_id = base64.urlsafe_b64encode(target_url.encode()).decode().strip("=")
    report_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        response = requests.get(report_url, headers=headers, timeout=10)

        if response.status_code == 404:
            return {"error": "Link này chưa có dữ liệu, hãy thử lại sau vài phút."}

        if response.status_code != 200:
            return {"error": f"VirusTotal API error: {response.status_code}"}

        result_data = response.json()
        stats = result_data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)

        total_bad = malicious + suspicious
        if total_bad >= 2:
            status = "DOC_HAI"
        elif total_bad == 1:
            status = "CANH_BAO"
        else:
            status = "AN_TOAN"

        return {
            "error": None,
            "status": status,
            "risk_score": total_bad,          # ← sửa: dùng total_bad
            "raw_stats": stats,
            "malicious_count": malicious,
            "suspicious_count": suspicious
        }

    except Exception as e:
        return {"error": str(e)}


def scan_file_with_virustotal(file_path):
    if not VIRUSTOTAL_API_KEY:
        return {"error": "Chưa cấu hình API Key VirusTotal"}

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()

    api_url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 404:
            return {
                "error": None,
                "status": "KHONG_XAC_DINH",
                "risk_score": 0,
                "hash": file_hash,
                "raw_stats": {},
                "malicious_count": 0,
                "suspicious_count": 0
            }

        if response.status_code != 200:
            return {"error": f"VirusTotal API error: {response.status_code}"}

        data = response.json()
        stats = data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)

        total_bad = malicious + suspicious
        if total_bad >= 2:
            status = "DOC_HAI"
        elif total_bad == 1:
            status = "CANH_BAO"
        else:
            status = "AN_TOAN"

        return {
            "error": None,
            "status": status,
            "risk_score": total_bad,          # ← sửa: dùng total_bad
            "hash": file_hash,
            "raw_stats": stats,
            "malicious_count": malicious,
            "suspicious_count": suspicious
        }

    except Exception as e:
        return {"error": str(e)}