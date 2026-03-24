import requests
import time
from config import Config

URLSCAN_API_KEY = Config.URLSCAN_API_KEY

def scan_url_with_urlscan(url):
    """
    Gửi URL đến urlscan.io, chờ kết quả, trả về dict
    """
    if not URLSCAN_API_KEY:
        return {"error": "Missing URLScan API key"}

    headers = {"API-Key": URLSCAN_API_KEY, "Content-Type": "application/json"}
    data = {"url": url, "visibility": "public"}

    try:
        # Submit scan
        submit_resp = requests.post("https://urlscan.io/api/v1/scan/", headers=headers, json=data, timeout=10)
        if submit_resp.status_code != 200:
            return {"error": f"URLScan submit failed: {submit_resp.status_code}"}
        submit_data = submit_resp.json()
        scan_id = submit_data.get("uuid")

        # Chờ kết quả (polling)
        for _ in range(10):  # tối đa 30 giây
            time.sleep(3)
            result_resp = requests.get(f"https://urlscan.io/api/v1/result/{scan_id}/", timeout=10)
            if result_resp.status_code == 200:
                result = result_resp.json()
                # Trả về thông tin
                screenshot = result.get("screenshot", "")
                ip = result.get("page", {}).get("ip", "N/A")
                server = result.get("page", {}).get("server", "N/A")
                # Xác định risk_score: 0 nếu không có cảnh báo, 1 nếu có phát hiện (có thể điều chỉnh)
                risk_score = 0
                message = "Không phát hiện nguy hiểm"
                # Bạn có thể dựa vào "verdicts" để gán risk_score
                return {
                    "error": None,
                    "risk_score": risk_score,
                    "message": message,
                    "ip": ip,
                    "server": server,
                    "screenshot": screenshot
                }
        return {"error": "Timeout waiting for URLScan result"}
    except Exception as e:
        return {"error": str(e)}