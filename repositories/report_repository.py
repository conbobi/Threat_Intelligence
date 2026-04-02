from services.supabase_client import supabase
from typing import Optional, Dict, Any, List
from datetime import datetime

def create_report(
    user_id: Optional[str],
    report_type: str,
    target: str,
    normalized_target: Optional[str] = None,
    reason: Optional[str] = None,
    note: Optional[str] = None
) -> Dict[str, Any]:
    """Tạo báo cáo mới."""
    data = {
        'user_id': user_id,
        'report_type': report_type,
        'target': target,
        'normalized_target': normalized_target,
        'reason': reason,
        'note': note,
        'status': 'PENDING'
    }
    result = supabase.table('user_reports').insert(data).execute()
    return result.data[0]

def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin một báo cáo theo ID."""
    result = supabase.table('user_reports').select('*').eq('id', report_id).execute()
    return result.data[0] if result.data else None

def get_reports_by_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy danh sách báo cáo của một người dùng."""
    result = supabase.table('user_reports') \
        .select('*') \
        .eq('user_id', user_id) \
        .order('created_at', desc=True) \
        .limit(limit) \
        .execute()
    return result.data

def get_all_reports(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả báo cáo (cho admin). Có thể lọc theo status."""
    query = supabase.table('user_reports').select('*').order('created_at', desc=True).limit(limit)
    if status:
        query = query.eq('status', status)
    result = query.execute()
    return result.data

def update_report_status(
    report_id: str,
    status: str,
    admin_note: Optional[str] = None,
    reviewed_by: Optional[str] = None
) -> Dict[str, Any]:
    """Cập nhật trạng thái báo cáo và ghi chú của admin."""
    data = {
        'status': status,
        'reviewed_at': datetime.utcnow().isoformat()
    }
    if admin_note is not None:
        data['admin_note'] = admin_note
    if reviewed_by is not None:
        data['reviewed_by'] = reviewed_by
    result = supabase.table('user_reports').update(data).eq('id', report_id).execute()
    return result.data[0]