import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from ..config import settings

logger = logging.getLogger(__name__)

async def fetch_news_for_market(query: str, days_back: int = 3) -> List[Dict]:
    """Fetches recent news articles from NewsAPI based on a query."""
    if not settings.NEWS_API_KEY:
        logger.warning("No NewsAPI key configured, skipping news fetch.")
        return []

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "language": "en",
        "sortBy": "relevancy",
        "apiKey": settings.NEWS_API_KEY,
        "pageSize": 10
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            
            results = []
            for article in articles:
                pub_date_str = article.get("publishedAt")
                pub_date = None
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    except:
                        pass
                
                results.append({
                    "headline": article.get("title", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "published_at": pub_date,
                    "url": article.get("url", ""),
                    "content": article.get("description", "")
                })
            
            return results
        except Exception as e:
            logger.error(f"Error fetching news for query '{query}': {e}")
            return []
