import requests
from urllib.parse import urlparse

def check_chongluadao(target_url):
    try:
        domain = urlparse(target_url).netloc
        if not domain:
            domain = target_url.replace("http://", "").replace("https://", "").split('/')[0]
    except:
        domain = target_url
        
    # Đã đổi sang link Githack siêu tốc độ, miễn nhiễm với nhà mạng VN
    cld_feed_url = "https://raw.githack.com/elliotwutingfeng/ChongLuaDao-Phishing-Blocklist/main/blocklist.txt"
    
    try:
        # Tăng thời gian chờ lên 10s để tránh báo lỗi oan
        response = requests.get(cld_feed_url, timeout=10)
        
        if response.status_code == 200:
            blacklist = response.text.splitlines()
            if domain in blacklist:
                return {
                    "source": "ChongLuaDao (VN)",
                    "status": "DOC_HAI",
                    "risk_score": 1,
                    "message": f"⚠️ Tên miền {domain} đã bị cộng đồng Việt Nam cảnh báo lừa đảo!"
                }
            else:
                return {
                    "source": "ChongLuaDao (VN)",
                    "status": "AN_TOAN",
                    "risk_score": 0,
                    "message": "✅ An toàn theo dữ liệu Chống Lừa Đảo VN."
                }
        else:
            return {"error": f"Lỗi máy chủ trả về mã: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Lỗi kết nối: {str(e)}"}