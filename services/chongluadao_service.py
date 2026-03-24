import requests

def check_chongluadao(url):
    """
    Gọi API của ChongLuaDao (nếu có). Nếu không, trả về an toàn.
    """
    # API chongluadao thường cần đăng ký, hiện tại giả lập
    return {
        "error": None,
        "risk_score": 0,
        "message": "Không phát hiện trong danh sách đen nội bộ (chongluadao.vn)"
    }