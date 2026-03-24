from services.supabase_client import supabase
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

def save_scan_result(
    user_id: Optional[str],
    scan_type: str,
    target: str,
    result_status: str,
    risk_score: int,
    advice: str,
    detail_json: Dict[str, Any],
    target_hash: Optional[str] = None,
    normalized_target: Optional[str] = None,
    is_guest: bool = False
) -> Dict[str, Any]:
    data = {
        'user_id': user_id,
        'scan_type': scan_type,
        'target': target,
        'target_hash': target_hash,
        'normalized_target': normalized_target,
        'result_status': result_status,
        'risk_score': risk_score,
        'advice': advice,
        'detail_json': detail_json,
        'is_guest': is_guest
    }
    result = supabase.table('scan_results').insert(data).execute()
    return result.data[0]

def get_recent_history_by_target(
    normalized_target: str,
    minutes: int = 5
) -> Optional[Dict[str, Any]]:
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    result = supabase.table('scan_results') \
        .select('*') \
        .eq('normalized_target', normalized_target) \
        .gte('created_at', cutoff.isoformat()) \
        .order('created_at', desc=True) \
        .limit(1) \
        .execute()
    return result.data[0] if result.data else None