from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from repositories.scan_repository import get_user_history

history_bp = Blueprint('history', __name__, url_prefix='/history')

@history_bp.route('/')
def history_page():
    user_id = session.get('user_id')
    if not user_id:
        flash('Vui lòng đăng nhập để xem lịch sử quét.', 'warning')
        return redirect(url_for('auth.login_page'))
    username = session.get('username', 'Người dùng')
    return render_template('user/history/history.html', user_id=user_id, username=username)

@history_bp.route('/api', methods=['GET'])
def get_history_api():
    """API trả về danh sách lịch sử quét dưới dạng JSON."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        history = get_user_history(user_id, limit=100)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500