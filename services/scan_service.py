import os
import time
from werkzeug.utils import secure_filename
from config import Config  # cần tạo file config.py để lấy UPLOAD_FOLDER
from services.virustotal_service import scan_url_with_virustotal, scan_file_with_virustotal
from services.google_sb_service import scan_url_with_google
from services.urlscan_service import scan_url_with_urlscan
from services.chongluadao_service import check_chongluadao
from services.recommendation_service import get_master_advice
from repositories.scan_repository import get_recent_history_by_target, save_scan_result

# Helper để chuẩn hóa URL (tạm thời đơn giản)
def normalize_url(url):
    return url.lower().strip()

def scan_url(url, user_id=None):
    # 1. Kiểm tra cache
    normalized = normalize_url(url)
    history = get_recent_history_by_target(normalized, minutes=5)  # 5 phút cache
    if history:
        return {
            "status": history.get("result_status"),
            "risk_score": history.get("risk_score"),
            "advice": history.get("advice"),
            "details": ["🗄️ <strong>Nguồn truy xuất:</strong> Dữ liệu đệm từ cơ sở dữ liệu Supabase.", "⚡ <strong>Tối ưu hóa:</strong> Bỏ qua gọi API (Đã có người quét trong 24h qua)."]
        }

    # 2. Gọi các API
    results_list = ["🌐 <strong>Nguồn truy xuất:</strong> Quét API Thời gian thực (Real-time).<br>---"]
    total_risk_score = 0
    raw_details = {}

    # VirusTotal
    vt_res = scan_url_with_virustotal(url)
    if "error" not in vt_res:
        stats = vt_res.get("raw_stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0) + stats.get("harmless", 0)
        vt_html = f"""<div class='mt-2 p-2 rounded border border-secondary' style='background-color: #1e293b; font-size: 0.85rem;'>
            <strong>📊 Phân tích chi tiết (Security vendors' analysis):</strong><br>
            <span class='text-danger'>🔴 Độc hại (Malicious): {malicious}</span> | 
            <span class='text-warning'>🟡 Khả nghi (Suspicious): {suspicious}</span> | 
            <span class='text-success'>🟢 An toàn (Undetected): {undetected}</span>
        </div>"""
        status_icon = "🔴" if vt_res.get('status') == "DOC_HAI" else ("🟡" if vt_res.get('status') == "CANH_BAO" else "🟢")
        results_list.append(f"{status_icon} <strong>VirusTotal:</strong> Báo cáo mức độ {vt_res.get('risk_score')}/96 rủi ro.{vt_html}")
        # Thay dòng cũ:
        # if vt_res.get('status') == "DOC_HAI":
        #     total_risk_score += 1
        # Thành:
        total_risk_score += vt_res.get("risk_score", 0)
        raw_details["virustotal"] = stats

    # Google Safe Browsing
    gg_res = scan_url_with_google(url)
    if "error" not in gg_res:
        status_icon = "🔴" if gg_res.get('risk_score') > 0 else "🟢"
        results_list.append(f"{status_icon} <strong>Google Safe Browsing:</strong> {gg_res.get('message')}")
        total_risk_score += gg_res.get('risk_score', 0)

    # URLScan.io
    us_res = scan_url_with_urlscan(url)
    if "error" not in us_res:
        status_icon = "🔴" if us_res.get('risk_score') > 0 else "🟢"
        ip_info = f"<br>📍 <strong>IP Máy chủ:</strong> {us_res.get('ip', 'N/A')} ({us_res.get('server', 'N/A')})"
        screenshot_html = ""
        screenshot_url = us_res.get('screenshot')
        if screenshot_url:
            screenshot_html = f"<div class='mt-2 text-center'><a href='{screenshot_url}' target='_blank'><img src='{screenshot_url}' alt='Screenshot' class='img-fluid rounded border border-secondary' style='max-height: 250px;'></a><br><small class='text-muted'>📸 Ảnh chụp trang web từ máy ảo (Click để xem to)</small></div>"
        results_list.append(f"{status_icon} <strong>Urlscan.io:</strong> {us_res.get('message')}{ip_info}{screenshot_html}")
        total_risk_score += us_res.get('risk_score', 0)

    # ChongLuaDao VN
    cld_res = check_chongluadao(url)
    if "error" not in cld_res:
        status_icon = "🔴" if cld_res.get('risk_score') > 0 else "🟢"
        results_list.append(f"{status_icon} <strong>ChongLuaDao VN:</strong> {cld_res.get('message')}")
        total_risk_score += cld_res.get('risk_score', 0)

    # 3. Kết luận
    if total_risk_score >= 2:
        final_status = "DOC_HAI"
    elif total_risk_score == 1:
        final_status = "CANH_BAO"
    else:
        final_status = "AN_TOAN"

    advice_text = get_master_advice(total_risk_score)

    results_list.append("---")
    # Lưu vào database
    save_scan_result(
        user_id=user_id,
        scan_type='url',
        target=url,
        result_status=final_status,
        risk_score=total_risk_score,
        advice=advice_text,
        detail_json=raw_details,
        normalized_target=normalized,
        is_guest=(user_id is None)
    )
    results_list.append("💾 <strong>Database:</strong> Đã lưu kết quả quét vào hệ thống Supabase thành công.")

    return {
        "status": final_status,
        "risk_score": total_risk_score,
        "advice": advice_text,
        "details": results_list
    }

def scan_file(file, user_id=None):
    filename = secure_filename(file.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)

    res = scan_file_with_virustotal(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    if "error" in res:
        return {"error": res["error"]}

    if res["status"] == "KHONG_XAC_DINH":
        advice_html = "⚠️ Tệp tin này chưa từng tồn tại trên Cơ sở dữ liệu của VirusTotal.<br>Khuyến nghị: Không nên mở nếu không rõ nguồn gốc."
        details_html = [
            f"📄 <strong>Tên file:</strong> {filename}",
            f"🔑 <strong>Mã SHA-256:</strong> {res['hash']}",
            "⚪ <strong>Trạng thái:</strong> Chưa có dữ liệu phân tích."
        ]
    else:
        advice_html = get_master_advice(res["risk_score"], is_file=True)
        status_icon = "🔴" if res['risk_score'] >= 2 else ("🟡" if res['risk_score'] == 1 else "🟢")
        stats = res.get('raw_stats', {})
        vt_html = f"""<div class='mt-2 p-2 rounded border border-secondary' style='background-color: #1e293b; font-size: 0.85rem;'>
            <strong>📊 Phân tích chi tiết (Security vendors' analysis):</strong><br>
            <span class='text-danger'>🔴 Độc hại: {stats.get('malicious', 0)}</span> | 
            <span class='text-warning'>🟡 Khả nghi: {stats.get('suspicious', 0)}</span> | 
            <span class='text-success'>🟢 An toàn: {stats.get('undetected', 0) + stats.get('harmless', 0)}</span>
        </div>"""
        details_html = [
            f"📄 <strong>Tên file:</strong> {filename}",
            f"🔑 <strong>Mã SHA-256:</strong> {res['hash']}",
            "🌐 <strong>Nguồn dữ liệu:</strong> VirusTotal API (Cloud Hash Lookup)",
            f"{status_icon} <strong>Kiểm định VirusTotal:</strong> Phát hiện {res['risk_score']}/70 phần mềm đánh giá độc hại.{vt_html}"
        ]

    return {
        "status": res["status"],
        "risk_score": res["risk_score"],
        "advice": advice_html,
        "details": details_html
    }