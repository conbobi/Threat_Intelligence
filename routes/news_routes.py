from flask import Blueprint, render_template, abort
from services.news_service import get_news_list, get_news_by_id

news_bp = Blueprint('news', __name__, url_prefix='/user')

@news_bp.route('/news')
def news_list():
    """Trang danh sách tin tức."""
    news_items = get_news_list(only_published=True)
    return render_template('user/news.html', news_list=news_items, active_page='news')

@news_bp.route('/news/<uuid:news_id>')   # thay int thành uuid
def news_detail(news_id):
    news = get_news_by_id(str(news_id))   # convert UUID sang string
    if not news or news.get('status') != 'published':
        abort(404)
    return render_template('user/news_detail.html', news=news, active_page='news')