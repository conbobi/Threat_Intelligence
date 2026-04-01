from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import admin_required
from services.news_service import get_news_list, create_news,get_news_list_for_admin

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', username=session.get('username'))

@admin_bp.route('/news')
@admin_bp.route('/news')
@admin_required
def news_list():
    news_list = get_news_list_for_admin(only_visible=False)  # admin xem cả bài ẩn
    return render_template('admin/news_list.html', news_list=news_list, username=session.get('username'))
@admin_bp.route('/news/create', methods=['GET', 'POST'])
@admin_required
def news_create():
    if request.method == 'GET':
        return render_template('admin/news_create.html', username=session.get('username'))

    title = request.form.get('tieu_de', '').strip()
    summary = request.form.get('mo_ta_ngan', '').strip()
    content = request.form.get('noi_dung_chi_tiet', '').strip()
    thumbnail = request.form.get('hinh_anh_minh_hoa', '').strip()
    status = request.form.get('trang_thai', 'published').strip()

    if not title or not summary or not content:
        flash('Vui lòng nhập đầy đủ tiêu đề, mô tả ngắn và nội dung chi tiết.', 'error')
        return render_template('admin/news_create.html', username=session.get('username'))

    result = create_news(
        title=title,
        summary=summary,
        content=content,
        thumbnail_url=thumbnail,
        status=status,
        author_id=session.get('user_id')
    )

    if result:
        flash('Đăng bài viết thành công!', 'success')
        return redirect(url_for('admin.news_list'))
    else:
        flash('Đăng bài thất bại. Xem log terminal để biết lỗi cụ thể.', 'error')
        return render_template('admin/news_create.html', username=session.get('username'))