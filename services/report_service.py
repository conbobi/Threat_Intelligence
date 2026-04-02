import re
from typing import Optional, Dict, Any, List
from repositories.report_repository import (
    create_report as repo_create_report,
    get_report_by_id,
    get_reports_by_user,
    get_all_reports,
    update_report_status
)
from services.scan_service import scan_url, scan_file  # import để quét URL/file

def normalize_target(target: str) -> str:
    """Chuẩn hóa target (loại bỏ http/https, www, dấu / cuối)."""
    target = re.sub(r'^https?://', '', target.lower().strip())
    target = re.sub(r'^www\.', '', target)
    target = target.rstrip('/')
    return target

def create_report(
    user_id: Optional[str],
    report_type: str,
    target: str,
    reason: Optional[str] = None,
    note: Optional[str] = None
) -> Dict[str, Any]:
    """Tạo báo cáo mới, tự động chuẩn hóa target, và quét nếu là URL."""
    if report_type not in ('url', 'file'):
        raise ValueError('report_type must be "url" or "file"')
    
    normalized = normalize_target(target) if report_type == 'url' else target
    
    # Tạo báo cáo
    report = repo_create_report(
        user_id=user_id,
        report_type=report_type,
        target=target,
        normalized_target=normalized,
        reason=reason,
        note=note
    )
    
    # Nếu là URL, thực hiện quét (có thể lưu thêm kết quả vào detail_json của report nếu cần)
    if report_type == 'url':
        # Quét URL bằng scan_service
        scan_result = scan_url(target, user_id=user_id)
        # Có thể lưu kết quả quét vào một bảng khác hoặc cập nhật vào report (tùy chọn)
        # Ở đây ta chỉ trả về cùng với report
        report['scan_result'] = scan_result
    elif report_type == 'file':
        # Đối với file, không thể quét ngay vì cần upload file, nhưng bạn có thể thiết kế thêm
        # Ở đây tạm thời bỏ qua
        pass
    
    return report

def get_user_reports(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy danh sách báo cáo của một người dùng."""
    return get_reports_by_user(user_id, limit)

def get_all_reports_for_admin(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Lấy tất cả báo cáo (admin). Có thể lọc theo status."""
    return get_all_reports(limit=limit, status=status)

def get_report_details(report_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết báo cáo."""
    return get_report_by_id(report_id)

def update_report(
    report_id: str,
    status: str,
    admin_note: Optional[str] = None,
    reviewed_by: Optional[str] = None
) -> Dict[str, Any]:
    """Cập nhật báo cáo (admin)."""
    if status not in ('PENDING', 'REVIEWING', 'RESOLVED', 'REJECTED'):
        raise ValueError('Invalid status')
    return update_report_status(report_id, status, admin_note, reviewed_by)