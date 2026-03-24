import requests
import hashlib
import os
from config import Config

VIRUSTOTAL_API_KEY = Config.VIRUSTOTAL_API_KEY
VIRUSTOTAL_URL = "https://www.virustotal.com/api/v3/"

def scan_url_with_virustotal(url):
    """
    Kiểm tra URL với VirusTotal API.
    Trả về dict:
    {
        'error': None hoặc thông báo lỗi,
        'status': 'DOC_HAI' | 'CANH_BAO' | 'AN_TOAN',
        'risk_score': int (số lượng engine phát hiện độc hại),
        'raw_stats': dict (malicious, suspicious, undetected, harmless)
    }
    """
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    # Cần encode URL
    import urllib.parse
    encoded_url = urllib.parse.quote(url, safe='')
    api_url = f"{VIRUSTOTAL_URL}urls/{encoded_url}"

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            undetected = stats.get("undetected", 0) + stats.get("harmless", 0)

            if malicious > 0:
                status = "DOC_HAI"
            elif suspicious > 0:
                status = "CANH_BAO"
            else:
                status = "AN_TOAN"

            return {
                "error": None,
                "status": status,
                "risk_score": malicious,
                "raw_stats": stats
            }
        elif response.status_code == 404:
            return {
                "error": None,
                "status": "AN_TOAN",
                "risk_score": 0,
                "raw_stats": {}
            }
        else:
            return {"error": f"VirusTotal API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def scan_file_with_virustotal(file_path):
    """
    Kiểm tra file với VirusTotal API (dùng hash).
    Trả về dict:
    {
        'error': None hoặc thông báo lỗi,
        'status': 'DOC_HAI' | 'AN_TOAN' | 'KHONG_XAC_DINH',
        'risk_score': int,
        'hash': str,
        'raw_stats': dict
    }
    """
    # Tính hash của file
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()

    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    api_url = f"{VIRUSTOTAL_URL}files/{file_hash}"

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            undetected = stats.get("undetected", 0) + stats.get("harmless", 0)

            if malicious > 0:
                status = "DOC_HAI"
            elif suspicious > 0:
                status = "CANH_BAO"
            else:
                status = "AN_TOAN"

            return {
                "error": None,
                "status": status,
                "risk_score": malicious,
                "hash": file_hash,
                "raw_stats": stats
            }
        elif response.status_code == 404:
            return {
                "error": None,
                "status": "KHONG_XAC_DINH",
                "risk_score": 0,
                "hash": file_hash,
                "raw_stats": {}
            }
        else:
            return {"error": f"VirusTotal API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}