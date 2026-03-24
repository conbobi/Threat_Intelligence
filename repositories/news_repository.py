from services.supabase_client import supabase
from typing import Optional, Dict, Any, List

def get_all_news(only_visible: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
    query = supabase.table('news_articles').select('*')
    if only_visible:
        query = query.eq('status', 'HIEN')
    query = query.order('created_at', desc=True).limit(limit)
    result = query.execute()
    return result.data

def create_news_article(
    title: str,
    summary: str,
    content: str,
    author_id: Optional[str],
    thumbnail_url: str = None,
    status: str = 'HIEN'
) -> Dict[str, Any]:
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