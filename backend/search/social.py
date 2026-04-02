"""Search for high-traffic social media references using Google Custom Search API."""
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SearchUnavailableError(Exception):
    """Raised when Google CSE is not configured or returns an API error."""


def search_social_references(product_name: str) -> list[dict]:
    """Return up to 3 reference links from xiaohongshu/instagram.

    Raises SearchUnavailableError if API key is missing or request fails.
    Returns empty list if no results found (not an error).
    """
    api_key = os.environ.get("GOOGLE_CSE_API_KEY", "")
    cx = os.environ.get("GOOGLE_CSE_CX", "")

    if not api_key or not cx:
        raise SearchUnavailableError("Google CSE API key not configured")

    query = f"{product_name} site:xiaohongshu.com OR site:instagram.com"

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=query, cx=cx, num=3, lr="lang_zh-TW").execute()
        items = result.get("items", [])
        return [
            {"title": item.get("title", ""), "url": item.get("link", "")}
            for item in items[:3]
        ]
    except HttpError as e:
        raise SearchUnavailableError(str(e)) from e
    except SearchUnavailableError:
        raise
    except Exception as e:
        raise SearchUnavailableError(str(e)) from e
