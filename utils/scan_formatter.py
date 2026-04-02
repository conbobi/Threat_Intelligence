# utils/scan_formatter.py
def format_vt_html(stats: dict) -> str:
    malicious = stats.get('malicious', 0)
    suspicious = stats.get('suspicious', 0)
    undetected = stats.get('undetected', 0) + stats.get('harmless', 0)
    return f"""<div class='mt-2 p-2 rounded border border-secondary' style='background-color: #1e293b; font-size: 0.85rem;'>
        <strong>📊 Phân tích chi tiết (Security vendors' analysis):</strong><br>
        <span class='text-danger'>🔴 Độc hại (Malicious): {malicious}</span> | 
        <span class='text-warning'>🟡 Khả nghi (Suspicious): {suspicious}</span> | 
        <span class='text-success'>🟢 An toàn (Undetected): {undetected}</span>
    </div>"""

def format_urlscan_screenshot(screenshot_url: str) -> str:
    if not screenshot_url:
        return ""
    return f"""<div class='mt-2 text-center'>
        <a href='{screenshot_url}' target='_blank'>
            <img src='{screenshot_url}' alt='Screenshot' class='img-fluid rounded border border-secondary' style='max-height: 250px;'>
        </a><br>
        <small class='text-muted'>📸 Ảnh chụp trang web từ máy ảo (Click để xem to)</small>
    </div>"""

def format_source_item(source_name: str, source_data: dict) -> str:
    if source_data.get('error'):
        return f"⚠️ <strong>{source_name}:</strong> {source_data['error']}"
    risk = source_data.get('risk_score', 0)
    status_icon = "🔴" if risk >= 2 else ("🟡" if risk == 1 else "🟢")
    msg = source_data.get('message', '')
    if source_name == "VirusTotal":
        stats = source_data.get('raw_stats', {})
        vt_html = format_vt_html(stats)
        return f"{status_icon} <strong>{source_name}:</strong> {msg}{vt_html}"
    elif source_name == "Urlscan.io":
        ip_info = f"<br>📍 <strong>IP Máy chủ:</strong> {source_data.get('ip', 'N/A')} ({source_data.get('server', 'N/A')})"
        screenshot_html = format_urlscan_screenshot(source_data.get('screenshot'))
        return f"{status_icon} <strong>{source_name}:</strong> {msg}{ip_info}{screenshot_html}"
    else:
        return f"{status_icon} <strong>{source_name}:</strong> {msg}"
    
def format_scan_result_for_api(clean_result: dict) -> dict:
    details = []
    if clean_result.get('from_cache'):
        details.append("🗄️ <strong>Nguồn truy xuất:</strong> Dữ liệu đệm từ cơ sở dữ liệu Supabase.")
        details.append("⚡ <strong>Tối ưu hóa:</strong> Bỏ qua gọi API (Đã có người quét trong 5 phút qua).")
    else:
        sources = clean_result.get('sources', {})
        for name, data in sources.items():
            # Gọi các hàm format riêng (ví dụ format_source_item)
            details.append(format_source_item(name, data))
        details.append("---")
        details.append("💾 <strong>Database:</strong> Đã lưu kết quả quét vào hệ thống Supabase thành công.")

    return {
        "status": clean_result['status'],
        "risk_score": clean_result['risk_score'],
        "advice": clean_result['advice'],
        "details": details
    }

def format_file_result(clean_result: dict) -> dict:
    details = []
    if clean_result.get('from_cache'):
        details.append("🗄️ <strong>Nguồn truy xuất:</strong> Dữ liệu đệm từ cơ sở dữ liệu Supabase.")
        details.append("⚡ <strong>Tối ưu hóa:</strong> Bỏ qua gọi API (Đã có người quét trong 5 phút qua).")
    else:
        sources = clean_result.get('sources', {})
        for name, data in sources.items():
            # Đối với file, nguồn là VirusTotal
            if name == 'VirusTotal':
                risk = data.get('risk_score', 0)
                status_icon = "🔴" if risk >= 2 else ("🟡" if risk == 1 else "🟢")
                msg = data.get('message', '')
                if data.get('status') == 'KHONG_XAC_DINH':
                    msg = "Chưa có dữ liệu phân tích từ VirusTotal."
                stats = data.get('raw_stats', {})
                vt_html = format_vt_html(stats) if stats else ""
                details.append(f"{status_icon} <strong>{name}:</strong> {msg}{vt_html}")
        details.append("---")
        details.append("💾 <strong>Database:</strong> Đã lưu kết quả quét vào hệ thống Supabase thành công.")
    return {
        "status": clean_result['status'],
        "risk_score": clean_result['risk_score'],
        "advice": clean_result['advice'],
        "details": details
    }