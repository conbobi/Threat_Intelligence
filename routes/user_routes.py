from flask import Blueprint, render_template, session
from flask import Blueprint, render_template, session, redirect, url_for, flash
from repositories.user_repository import get_profile_by_id

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    return render_template(
        'user/index.html',
        username=session.get('username'),
        user_id=session.get('user_id'),
        role=session.get('role')
    )



@user_bp.route('/report')
def report():
    return render_template('user/report.html', active_page='report')

@user_bp.route('/history')
def history():
    """Trang lịch sử quét của người dùng."""
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem lịch sử.', 'warning')
        return redirect(url_for('auth.login_page'))
    # Tạm thời chỉ hiển thị khung, sau sẽ thêm logic lấy dữ liệu
    return render_template('user/history.html', active_page='history')

@user_bp.route('/guide')
def guide():
    """Trang hướng dẫn."""
    return render_template('user/guide.html', active_page='guide')
@user_bp.route('/profile')
def profile():
    """Hiển thị thông tin cá nhân của người dùng."""
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem trang cá nhân.', 'warning')
        return redirect(url_for('auth.login_page'))
    
    user_id = session['user_id']
    profile = get_profile_by_id(user_id)
    if not profile:
        flash('Không tìm thấy thông tin người dùng.', 'danger')
        return redirect(url_for('user.index'))
    
    return render_template('user/profile.html', profile=profile)