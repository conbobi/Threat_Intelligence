# tests/test_auth.py
import pytest
import json
from unittest.mock import patch, MagicMock
from config import Config

# ==================== TEST ĐĂNG KÝ ====================

def test_register_success(client):
    """Đăng ký thành công với dữ liệu hợp lệ."""
    with patch('services.auth_service.supabase') as mock_supabase:
        # Mock supabase.auth.sign_up trả về user
        mock_user = MagicMock()
        mock_user.user.id = "test-user-id"
        mock_supabase.auth.sign_up.return_value = mock_user

        # Mock create_profile
        with patch('services.auth_service.create_profile') as mock_create:
            mock_create.return_value = {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'username': 'testuser'
            }

            response = client.post('/auth/register',
                data=json.dumps({
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Đăng ký thành công'

def test_register_missing_fields(client):
    """Thiếu trường dữ liệu (username, email, password)."""
    response = client.post('/auth/register',
        data=json.dumps({'email': 'test@example.com'}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Vui lòng nhập đầy đủ thông tin' in data['message']

def test_register_invalid_email(client):
    """Email không đúng định dạng."""
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'test',
            'email': 'invalid-email',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Email không hợp lệ' in data['message']

def test_register_short_password(client):
    """Mật khẩu dưới 6 ký tự."""
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'test',
            'email': 'test@example.com',
            'password': '12345'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Mật khẩu phải có ít nhất 6 ký tự' in data['message']

def test_register_duplicate_email(client):
    """Email đã tồn tại (supabase trả lỗi)."""
    with patch('services.auth_service.supabase') as mock_supabase:
        mock_supabase.auth.sign_up.side_effect = Exception('User already registered')
        response = client.post('/auth/register',
            data=json.dumps({
                'username': 'test',
                'email': 'test@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Email đã được sử dụng' in data['message']

# ==================== TEST ĐĂNG NHẬP ====================

def test_login_success_regular_user(client):
    """Đăng nhập thành công với user thường (không phải admin)."""
    with patch('services.auth_service.supabase') as mock_supabase:
        # Mock supabase.auth.sign_in_with_password
        mock_user = MagicMock()
        mock_user.user.id = "user-123"
        mock_supabase.auth.sign_in_with_password.return_value = mock_user

        # Mock get_profile_by_id
        with patch('services.auth_service.get_profile_by_id') as mock_profile:
            mock_profile.return_value = {
                'id': 'user-123',
                'email': 'user@example.com',
                'role': 'USER',
                'username': 'testuser',
                'status': 'ACTIVE'
            }

            response = client.post('/auth/login',
                data=json.dumps({'email': 'user@example.com', 'password': 'password123'}),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['redirect'] == '/'

            # Kiểm tra session có được set không (cần dùng client để truy cập session)
            with client.session_transaction() as sess:
                assert sess['user_id'] == 'user-123'
                assert sess['role'] == 'USER'
                assert sess['email'] == 'user@example.com'
                assert sess['username'] == 'testuser'

def test_login_admin_default(client, monkeypatch):
    """Đăng nhập admin mặc định (từ Config)."""
    monkeypatch.setattr(Config, 'ADMIN_EMAIL', 'admin@system.com')
    monkeypatch.setattr(Config, 'ADMIN_PASSWORD', 'admin123')

    with patch('services.auth_service.get_profile_by_email') as mock_get:
        mock_get.return_value = None
        with patch('services.auth_service.create_profile') as mock_create:
            mock_create.return_value = {
                'id': 'admin-uuid-123',  # sử dụng UUID hợp lệ
                'email': 'admin@system.com',
                'role': 'ADMIN',
                'username': 'admin'
            }
            with patch('services.auth_service.get_profile_by_id') as mock_get_by_id:
                mock_get_by_id.return_value = {
                    'id': 'admin-uuid-123',
                    'email': 'admin@system.com',
                    'role': 'ADMIN',
                    'username': 'admin',
                    'status': 'ACTIVE'
                }
                response = client.post('/auth/login',
                    data=json.dumps({'email': 'admin@system.com', 'password': 'admin123'}),
                    content_type='application/json'
                )
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['redirect'] == '/'

                with client.session_transaction() as sess:
                    assert sess['role'] == 'ADMIN'
                    assert sess['email'] == 'admin@system.com'
def test_login_wrong_credentials(client):
    """Đăng nhập sai email/mật khẩu."""
    with patch('services.auth_service.supabase') as mock_supabase:
        mock_supabase.auth.sign_in_with_password.side_effect = Exception('Invalid login')
        response = client.post('/auth/login',
            data=json.dumps({'email': 'wrong@example.com', 'password': 'wrong'}),
            content_type='application/json'
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Đăng nhập thất bại' in data['message']
def test_login_missing_fields(client):
    """Thiếu email hoặc mật khẩu."""
    response = client.post('/auth/login',
        data=json.dumps({'email': 'test@example.com'}),
        content_type='application/json'
    )
    assert response.status_code == 401  # sửa thành 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Vui lòng nhập email và mật khẩu' in data['message']
# ==================== TEST ĐĂNG XUẤT ====================

def test_logout(client):
    """Đăng xuất xoá session và redirect về login."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'some-id'
        sess['role'] = 'USER'

    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'role' not in sess
    # Kiểm tra redirect có dẫn đến login page (tuỳ logic)
    assert 'Đăng nhập'.encode('utf-8') in response.data # sửa thành bytes
# ==================== TEST ROUTE HIỂN THỊ FORM ====================

def test_login_page(client):
    """GET /auth/login hiển thị form."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'form' in response.data.lower() or b'login' in response.data.lower()

def test_register_page(client):
    """GET /auth/register hiển thị form."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'form' in response.data.lower() or b'register' in response.data.lower()