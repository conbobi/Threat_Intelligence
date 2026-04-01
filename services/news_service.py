from repositories.news_repository import get_all_news, create_news_article, get_news_by_id as repo_get_news_by_id

def get_news_list(only_published=True):
    """Lấy danh sách bài viết công khai cho user."""
    # only_published = True -> chỉ lấy bài published
    return get_all_news(only_visible=only_published)

def get_news_list_for_admin(only_visible=False):
    """Lấy danh sách bài viết cho admin (xem cả bài ẩn)."""
    return get_all_news(only_visible=only_visible)

def create_news(title, summary, content, thumbnail_url, status, author_id):
    return create_news_article(
        title=title,
        summary=summary,
        content=content,
        author_id=author_id,
        thumbnail_url=thumbnail_url,
        status=status
    )

def get_news_by_id(news_id):
    return repo_get_news_by_id(news_id)