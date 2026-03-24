from repositories.news_repository import get_all_news, create_news_article

def get_news_list(only_visible=True):
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