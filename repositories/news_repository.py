from typing import Optional, Dict, Any, List
from services.supabase_client import supabase

def get_all_news(only_visible: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lấy danh sách bài viết.
    - only_visible=True: chỉ lấy bài có status='published'
    - only_visible=False: lấy tất cả (dành cho admin)
    """
    query = supabase.table('news_articles').select('*')
    if only_visible:
        query = query.eq('status', 'published')
    query = query.order('created_at', desc=True).limit(limit)
    result = query.execute()
    return result.data

def get_news_by_id(news_id: str) -> Optional[Dict[str, Any]]:
    """Lấy một bài viết theo ID."""
    result = supabase.table('news_articles').select('*').eq('id', news_id).execute()
    return result.data[0] if result.data else None

def create_news_article(
    title: str,
    summary: str,
    content: str,
    author_id: Optional[str],
    thumbnail_url: str = None,
    status: str = 'published'
) -> Dict[str, Any]:
    """Tạo bài viết mới."""
    data = {
        'title': title,
        'summary': summary,
        'content': content,
        'author_id': author_id,
        'thumbnail_url': thumbnail_url,
        'status': status
    }
    result = supabase.table('news_articles').insert(data).execute()
    return result.data[0]

def update_news_article(news_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật bài viết (chỉ admin).
    data có thể chứa các field: title, summary, content, thumbnail_url, status
    """
    result = supabase.table('news_articles').update(data).eq('id', news_id).execute()
    if result.data:
        return result.data[0]
    raise ValueError(f"Article with id {news_id} not found")

def delete_news_article(news_id: str) -> None:
    """Xóa bài viết (chỉ admin)."""
    result = supabase.table('news_articles').delete().eq('id', news_id).execute()
    if not result.data:
        raise ValueError(f"Article with id {news_id} not found")