from flask import Blueprint, render_template, session, redirect, url_for

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
def profile_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    user_info = {
        'id': session.get('user_id'),
        'email': session.get('email'),
        'username': session.get('username'),
        'role': session.get('role')
    }
    return render_template('user/profile/profile.html', user=user_info)