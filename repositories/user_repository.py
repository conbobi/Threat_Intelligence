from typing import Optional, Dict, Any
from services.supabase_client import supabase


def get_profile_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin profile theo user_id (uuid)"""
    result = supabase.table('profiles').select('*').eq('id', user_id).execute()
    return result.data[0] if result.data else None


def get_profile_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin profile theo email"""
    result = supabase.table('profiles').select('*').eq('email', email).execute()
    return result.data[0] if result.data else None


def create_profile(
    user_id: str,
    email: str,
    username: str = None,
    full_name: str = None
) -> Dict[str, Any]:
    """Tạo mới profile sau khi user đã có tài khoản trong Supabase Auth"""
    data = {
        'id': user_id,
        'email': email,
        'username': username or (email.split('@')[0] if email else None),
        'full_name': full_name,
        'role': 'USER',
        'status': 'ACTIVE'
    }
    result = supabase.table('profiles').insert(data).execute()
    return result.data[0]


def update_profile(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Cập nhật profile"""
    result = supabase.table('profiles').update(updates).eq('id', user_id).execute()
    return result.data[0] if result.data else None


def get_user_role(user_id: str) -> Optional[str]:
    """Lấy role của user"""
    profile = get_profile_by_id(user_id)
    return profile.get('role') if profile else None


def is_admin(user_id: str) -> bool:
    """Kiểm tra user có phải admin không"""
    role = get_user_role(user_id)
    return role == 'ADMIN'