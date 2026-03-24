from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('user/auth/login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('user/auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    result = register_user(username, email, password)

    if result.get('success'):
        return jsonify(result), 200
    return jsonify(result), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    result = login_user(email, password)
    if result['success']:
        session['user_id'] = result['user']['id']
        session['role'] = result['user']['role']
        session['email'] = result['user']['email']
        session['username'] = result['user'].get('username', '')
        return jsonify({'success': True, 'redirect': '/'})

    return jsonify({'success': False, 'message': result['message']}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('auth.login_page'))