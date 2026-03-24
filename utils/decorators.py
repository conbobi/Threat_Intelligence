from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'ADMIN':
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('auth.login_page'))  # chuyển về trang login user
        return f(*args, **kwargs)
    return decorated_function