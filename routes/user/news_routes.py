from flask import Blueprint, render_template, abort
from services.news_service import (
    get_news_list_for_user,
    get_news_details_for_user
)

user_news_bp = Blueprint('user_news', __name__, url_prefix='/user')

@user_news_bp.route('/news')
def news_list():
    """Trang danh sách tin tức cho user."""
    news_items = get_news_list_for_user(limit=50)
    return render_template(
        '/user/news/news.html',
        news_list=news_items,
        active_page='news'
    )

@user_news_bp.route('/news/<uuid:news_id>')
def news_detail(news_id):
    """Trang chi tiết bài viết cho user."""
    news = get_news_details_for_user(str(news_id))
    if not news:
        abort(404)

    return render_template(
        '/user/news/news_detail.html',
        news=news,
        active_page='news'
    )