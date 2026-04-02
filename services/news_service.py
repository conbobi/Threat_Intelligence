from typing import Optional, Dict, Any, List
from repositories.news_repository import (
    get_all_news,
    get_news_by_id as repo_get_news_by_id,
    create_news_article,
    update_news_article,
    delete_news_article
)

# ------------------- User (public) -------------------
def get_news_list_for_user(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lấy danh sách bài viết cho người dùng (chỉ bài published).
    """
    return get_all_news(only_visible=True, limit=limit)

def get_news_details_for_user(news_id: str) -> Optional[Dict[str, Any]]:
    """
    Lấy chi tiết bài viết cho người dùng, chỉ trả về nếu bài viết có status='published'.
    """
    article = repo_get_news_by_id(news_id)
    if article and article.get('status') == 'published':
        return article
    return None

# ------------------- Admin -------------------
def get_news_list_for_admin(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Lấy danh sách tất cả bài viết cho admin (bao gồm cả bài nháp, ẩn).
    """
    return get_all_news(only_visible=False, limit=limit)

def get_news_details_for_admin(news_id: str) -> Optional[Dict[str, Any]]:
    """
    Lấy chi tiết bài viết cho admin (không quan tâm status).
    """
    return repo_get_news_by_id(news_id)

def create_news(
    title: str,
    summary: str,
    content: str,
    author_id: Optional[str],
    thumbnail_url: str = None,
    status: str = 'published'
) -> Dict[str, Any]:
    """
    Admin tạo bài viết mới.
    """
    return create_news_article(
        title=title,
        summary=summary,
        content=content,
        author_id=author_id,
        thumbnail_url=thumbnail_url,
        status=status
    )

def edit_news(news_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Admin sửa bài viết.
    data có thể là một subset các field: title, summary, content, thumbnail_url, status.
    """
    return update_news_article(news_id, data)

def delete_news(news_id: str) -> None:
    """
    Admin xóa bài viết.
    """
    delete_news_article(news_id)