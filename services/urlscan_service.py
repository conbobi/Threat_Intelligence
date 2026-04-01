import requests
import time
from config import Config

URLSCAN_API_KEY = Config.URLSCAN_API_KEY

def scan_url_with_urlscan(url):
    if not URLSCAN_API_KEY:
        return {"error": "Missing URLScan API key"}

    headers = {"API-Key": URLSCAN_API_KEY, "Content-Type": "application/json"}
    data = {"url": url, "visibility": "public"}

    try:
        # Submit
        submit_resp = requests.post("https://urlscan.io/api/v1/scan/", headers=headers, json=data, timeout=10)
        if submit_resp.status_code != 200:
            return {"error": f"URLScan submit failed: {submit_resp.status_code}"}
        submit_data = submit_resp.json()
        scan_id = submit_data.get("uuid")

        # Polling
        for _ in range(10):
            time.sleep(3)
            result_resp = requests.get(f"https://urlscan.io/api/v1/result/{scan_id}/", timeout=10)
            if result_resp.status_code == 200:
                result = result_resp.json()
                verdicts = result.get("verdicts", {})
                # risk_score = 1 nếu có phát hiện độc hại
                risk_score = 1 if verdicts.get("malicious", False) else 0
                return {
                    "error": None,
                    "risk_score": risk_score,
                    "message": "Cảnh báo phát hiện nguy hiểm" if risk_score else "Không phát hiện nguy hiểm",
                    "ip": result.get("page", {}).get("ip", "N/A"),
                    "server": result.get("page", {}).get("server", "N/A"),
                    "screenshot": result.get("screenshot", "")
                }
        return {"error": "Timeout waiting for URLScan result"}
    except Exception as e:
        return {"error": str(e)}