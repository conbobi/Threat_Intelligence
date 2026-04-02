import os
import hashlib
import logging
from werkzeug.utils import secure_filename
from config import Config
from services.virustotal_service import scan_url_with_virustotal, scan_file_with_virustotal
from services.google_sb_service import scan_url_with_google
from services.urlscan_service import scan_url_with_urlscan
from services.chongluadao_service import check_chongluadao
from services.recommendation_service import get_master_advice
from repositories.scan_repository import get_recent_history_by_target, save_scan_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_url(url: str) -> str:
    return url.lower().strip()

def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def collect_url_scan_sources(url: str) -> dict:
    """Gọi tất cả nguồn cho URL, trả về dict các kết quả thô."""
    sources = {}
    vt = scan_url_with_virustotal(url)
    sources['VirusTotal'] = vt
    gg = scan_url_with_google(url)
    sources['Google Safe Browsing'] = gg
    us = scan_url_with_urlscan(url)
    sources['Urlscan.io'] = us
    cld = check_chongluadao(url)
    sources['ChongLuaDao VN'] = cld
    return sources

def decide_url_final_result(sources: dict) -> tuple:
    """
    Quyết định status và risk_score dựa trên các nguồn.
    Ưu tiên VirusTotal nếu nó phát hiện nguy cơ.
    Trả về (status, risk_score)
    """
    vt = sources.get('VirusTotal')
    if vt and not vt.get('error'):
        vt_status = vt.get('status')
        vt_risk = vt.get('risk_score', 0)
        if vt_status in ('DOC_HAI', 'CANH_BAO'):
            logger.info(f"✅ VirusTotal phát hiện nguy cơ -> final_status={vt_status}, final_risk={vt_risk}")
            return vt_status, vt_risk
    # Nếu VirusTotal an toàn hoặc lỗi, tổng hợp từ các nguồn khác
    total_risk = 0
    for name, res in sources.items():
        if name != 'VirusTotal' and not res.get('error'):
            total_risk += res.get('risk_score', 0)
    if total_risk >= 2:
        return 'DOC_HAI', total_risk
    elif total_risk == 1:
        return 'CANH_BAO', total_risk
    else:
        return 'AN_TOAN', total_risk

def scan_url(url: str, user_id=None):
    normalized = normalize_url(url)
    logger.info(f"🔍 Bắt đầu quét URL: {url} (normalized: {normalized})")

    # Cache
    history = get_recent_history_by_target(normalized, minutes=5)
    if history:
        logger.info(f"📦 Cache hit: status={history.get('result_status')}, risk_score={history.get('risk_score')}")
        return {
            "status": history.get("result_status"),
            "risk_score": history.get("risk_score"),
            "advice": history.get("advice"),
            "from_cache": True,
            "sources": {},
            "target": url,
            "normalized_target": normalized
        }

    sources = collect_url_scan_sources(url)
    final_status, final_risk = decide_url_final_result(sources)
    advice_text = get_master_advice(final_risk)

    # Lưu database
    detail_json = {k: v for k, v in sources.items() if not v.get('error')}
    save_scan_result(
        user_id=user_id,
        scan_type='url',
        target=url,
        result_status=final_status,
        risk_score=final_risk,
        advice=advice_text,
        detail_json=detail_json,
        normalized_target=normalized,
        is_guest=(user_id is None)
    )

    return {
        "status": final_status,
        "risk_score": final_risk,
        "advice": advice_text,
        "from_cache": False,
        "sources": sources,
        "target": url,
        "normalized_target": normalized
    }
def decide_file_final_result(sources: dict) -> tuple:
    vt = sources.get('VirusTotal')
    if vt and not vt.get('error'):
        vt_status = vt.get('status')
        vt_risk = vt.get('risk_score', 0)
        # Nếu VirusTotal xác định là KHONG_XAC_DINH thì vẫn coi như an toàn tạm thời?
        if vt_status == 'KHONG_XAC_DINH':
            # Chưa có dữ liệu -> không thể kết luận, trả về AN_TOAN?
            return 'AN_TOAN', 0
        elif vt_status in ('DOC_HAI', 'CANH_BAO'):
            logger.info(f"✅ VirusTotal file phát hiện nguy cơ -> final_status={vt_status}, final_risk={vt_risk}")
            return vt_status, vt_risk
    # Nếu có lỗi hoặc không xác định, coi như an toàn (hoặc có thể trả lỗi)
    return 'AN_TOAN', 0
def scan_file(file, user_id=None):
    filename = secure_filename(file.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    try:
        file_hash = compute_file_hash(file_path)
        # Cache dựa trên hash (normalized_target là hash)
        history = get_recent_history_by_target(file_hash, minutes=5)
        if history:
            logger.info(f"📦 File cache hit: status={history.get('result_status')}, risk_score={history.get('risk_score')}")
            return {
                "status": history.get("result_status"),
                "risk_score": history.get("risk_score"),
                "advice": history.get("advice"),
                "from_cache": True,
                "sources": {},
                "target": filename,
                "hash": file_hash
            }
        sources = collect_file_scan_sources(file_path)
        final_status, final_risk = decide_file_final_result(sources)
        advice_text = get_master_advice(final_risk, is_file=True)
        detail_json = {k: v for k, v in sources.items() if not v.get('error')}
        save_scan_result(
            user_id=user_id,
            scan_type='file',
            target=filename,
            target_hash=file_hash,
            result_status=final_status,
            risk_score=final_risk,
            advice=advice_text,
            detail_json=detail_json,
            normalized_target=file_hash,
            is_guest=(user_id is None)
        )
        return {
            "status": final_status,
            "risk_score": final_risk,
            "advice": advice_text,
            "from_cache": False,
            "sources": sources,
            "target": filename,
            "hash": file_hash
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
def collect_file_scan_sources(file_path: str) -> dict:
    """Gọi VirusTotal cho file, trả về dict kết quả thô."""
    res = scan_file_with_virustotal(file_path)
    # res có thể có 'error' hoặc các trường khác
    return {'VirusTotal': res}