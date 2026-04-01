from services.supabase_client import supabase
from typing import Optional, Dict, Any, List

def get_all_news(only_visible: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy danh sách bài viết (cho user)."""
    query = supabase.table('news_articles').select('*')
    if only_visible:
        query = query.eq('status', 'published')
    query = query.order('created_at', desc=True).limit(limit)
    result = query.execute()
    return result.data

def create_news_article(
    title: str,
    summary: str,
    content: str,
    author_id: Optional[str],
    thumbnail_url: str = None,
    status: str = 'published'
) -> Dict[str, Any]:
    """Tạo bài viết mới (cho admin)."""
    data = {
        'title': title,
        'summary': summary,
        'content': content,
        'author_id': author_id,
        'thumbnail_url': thumbnail_url,
        'status': status
    }
    print(f"Inserting news with status: {status}")  # Thêm dòng này
    result = supabase.table('news_articles').insert(data).execute()
    return result.data[0]

def get_news_by_id(news_id: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('news_articles').select('*').eq('id', news_id).execute()
    return result.data[0] if result.data else None