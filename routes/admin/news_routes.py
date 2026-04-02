from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from utils.decorators import admin_required
from services.news_service import (
    get_news_list_for_admin,
    get_news_details_for_admin,
    create_news,
    edit_news,
    delete_news
)

admin_news_bp = Blueprint('admin_news', __name__, url_prefix='/admin/news')

ALLOWED_STATUSES = {'published', 'draft', 'hidden'}


@admin_news_bp.route('/', methods=['GET'])
@admin_required
def news_list():
    """Danh sách tất cả bài viết cho admin."""
    news_list = get_news_list_for_admin(limit=100)
    return render_template(
        'admin/news/news_list.html',
        news_list=news_list,
        username=session.get('username')
    )


@admin_news_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def news_create():
    """Tạo bài viết mới."""
    if request.method == 'GET':
        return render_template(
            'admin/news/news_create.html',
            username=session.get('username'),
            form_data={
                'title': '',
                'summary': '',
                'content': '',
                'thumbnail_url': '',
                'status': 'published'
            }
        )

    title = request.form.get('tieu_de', '').strip()
    summary = request.form.get('mo_ta_ngan', '').strip()
    content = request.form.get('noi_dung_chi_tiet', '').strip()
    thumbnail_url = request.form.get('hinh_anh_minh_hoa', '').strip()
    status = request.form.get('trang_thai', 'published').strip()

    form_data = {
        'title': title,
        'summary': summary,
        'content': content,
        'thumbnail_url': thumbnail_url,
        'status': status
    }

    if not title or not summary or not content:
        flash('Vui lòng nhập đầy đủ tiêu đề, mô tả ngắn và nội dung chi tiết.', 'error')
        return render_template(
            'admin/news/news_create.html',
            username=session.get('username'),
            form_data=form_data
        )

    if status not in ALLOWED_STATUSES:
        flash('Trạng thái bài viết không hợp lệ.', 'error')
        return render_template(
            'admin/news/news_create.html',
            username=session.get('username'),
            form_data=form_data
        )

    try:
        create_news(
            title=title,
            summary=summary,
            content=content,
            author_id=session.get('user_id'),
            thumbnail_url=thumbnail_url or None,
            status=status
        )
        flash('Đăng bài viết thành công!', 'success')
        return redirect(url_for('admin_news.news_list'))
    except Exception as e:
        flash(f'Đăng bài thất bại: {str(e)}', 'error')
        return render_template(
            'admin/news/news_create.html',
            username=session.get('username'),
            form_data=form_data
        )


@admin_news_bp.route('/<uuid:news_id>/edit', methods=['GET', 'POST'])
@admin_required
def news_edit(news_id):
    """Sửa bài viết."""
    article = get_news_details_for_admin(str(news_id))
    if not article:
        abort(404)

    if request.method == 'GET':
        return render_template(
            'admin/news/news_edit.html',
            news=article,
            username=session.get('username')
        )

    data = {
        'title': request.form.get('tieu_de', '').strip(),
        'summary': request.form.get('mo_ta_ngan', '').strip(),
        'content': request.form.get('noi_dung_chi_tiet', '').strip(),
        'thumbnail_url': request.form.get('hinh_anh_minh_hoa', '').strip() or None,
        'status': request.form.get('trang_thai', 'published').strip()
    }

    if not data['title'] or not data['summary'] or not data['content']:
        flash('Vui lòng nhập đầy đủ tiêu đề, mô tả ngắn và nội dung chi tiết.', 'error')
        updated_article = {**article, **data}
        return render_template(
            'admin/news/news_edit.html',
            news=updated_article,
            username=session.get('username')
        )

    if data['status'] not in ALLOWED_STATUSES:
        flash('Trạng thái bài viết không hợp lệ.', 'error')
        updated_article = {**article, **data}
        return render_template(
            'admin/news/news_edit.html',
            news=updated_article,
            username=session.get('username')
        )

    try:
        edit_news(str(news_id), data)
        flash('Cập nhật bài viết thành công!', 'success')
        return redirect(url_for('admin_news.news_list'))
    except Exception as e:
        flash(f'Cập nhật bài viết thất bại: {str(e)}', 'error')
        updated_article = {**article, **data}
        return render_template(
            'admin/news/news_edit.html',
            news=updated_article,
            username=session.get('username')
        )


@admin_news_bp.route('/<uuid:news_id>/delete', methods=['POST'])
@admin_required
def news_delete(news_id):
    """Xóa bài viết."""
    try:
        delete_news(str(news_id))
        flash('Xóa bài viết thành công!', 'success')
    except Exception as e:
        flash(f'Xóa bài viết thất bại: {str(e)}', 'error')

    return redirect(url_for('admin_news.news_list'))