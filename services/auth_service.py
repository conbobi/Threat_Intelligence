import re
from services.supabase_client import supabase
from repositories.user_repository import (
    create_profile,
    get_profile_by_email,
    get_profile_by_id,
)
from config import Config


def register_user(username, email, password):
    """Đăng ký người dùng mới bằng email/password."""
    if not username or not email or not password:
        return {'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {'success': False, 'message': 'Email không hợp lệ'}

    if len(password) < 6:
        return {'success': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'}

    existing = get_profile_by_email(email)
    if existing:
        return {'success': False, 'message': 'Email đã được đăng ký'}

    try:
        auth_result = supabase.auth.sign_up({
            'email': email,
            'password': password
        })

        if not auth_result or not auth_result.user:
            return {'success': False, 'message': 'Đăng ký thất bại'}

        user_id = auth_result.user.id

        # Tạo profile trong bảng profiles
        create_profile(user_id, email, username)

        return {
            'success': True,
            'message': 'Đăng ký thành công'
        }

    except Exception as e:
        error_msg = str(e)
        if 'User already registered' in error_msg or 'email_address' in error_msg:
            return {'success': False, 'message': 'Email đã được sử dụng'}
        return {'success': False, 'message': f'Lỗi hệ thống: {error_msg}'}


def login_user(email, password):
    """Đăng nhập bằng email/password."""
    if not email or not password:
        return {'success': False, 'message': 'Vui lòng nhập email và mật khẩu'}

    # Admin mặc định
    if email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD:
        profile = get_profile_by_email(email)
        if not profile:
            admin_id = 'admin-001'
            create_profile(admin_id, email, 'admin')
            profile = get_profile_by_id(admin_id)

        return {
            'success': True,
            'user': {
                'id': profile['id'],
                'email': profile['email'],
                'role': profile.get('role', 'ADMIN'),
                'username': profile.get('username', 'admin')
            }
        }

    try:
        auth_result = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        if not auth_result or not auth_result.user:
            return {'success': False, 'message': 'Sai email hoặc mật khẩu'}

        user_id = auth_result.user.id
        profile = get_profile_by_id(user_id)

        if not profile:
            return {'success': False, 'message': 'Không tìm thấy hồ sơ người dùng'}

        if profile.get('status') == 'BLOCKED':
            return {'success': False, 'message': 'Tài khoản đã bị khóa'}

        return {
            'success': True,
            'user': {
                'id': profile['id'],
                'email': profile['email'],
                'role': profile.get('role', 'USER'),
                'username': profile.get('username', '')
            }
        }

    except Exception as e:
        return {'success': False, 'message': f'Đăng nhập thất bại: {str(e)}'}