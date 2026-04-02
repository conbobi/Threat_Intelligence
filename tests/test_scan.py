#!/usr/bin/env python3
"""
Test script để kiểm tra scan URL với VirusTotal.
Sử dụng link test: http://testsafebrowsing.appspot.com/s/phishing.html
"""

import sys
import os

# Thêm đường dẫn project vào sys.path để import module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.virustotal_service import scan_url_with_virustotal

TEST_URL = "http://testsafebrowsing.appspot.com/s/phishing.html"


def test_phishing_url():
    """Kiểm tra URL phishing có được phát hiện đúng không."""
    print(f"Đang kiểm tra URL: {TEST_URL}")

    result = scan_url_with_virustotal(TEST_URL)

    if result.get("error"):
        print(f"❌ Lỗi: {result['error']}")
        return False

    status = result.get("status")
    malicious = result.get("malicious_count", 0)
    suspicious = result.get("suspicious_count", 0)
    risk_score = result.get("risk_score", 0)

    print(f"Kết quả: status={status}, malicious={malicious}, suspicious={suspicious}, risk_score={risk_score}")

    # Kiểm tra: Phải phát hiện là độc hại hoặc cảnh báo (không an toàn)
    if status in ("DOC_HAI", "CANH_BAO"):
        print("✅ Test thành công: URL đã được phát hiện đúng.")
        return True
    else:
        print(f"❌ Test thất bại: URL đáng lẽ phải là DOC_HAI/CANH_BAO nhưng lại là {status}.")
        return False


if __name__ == "__main__":
    success = test_phishing_url()
    sys.exit(0 if success else 1)