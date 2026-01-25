from typing import Any

from canrotbot.essentials.libraries.network import get_client
from canrotbot.llm.tools import register_tool

ANILIST_API = "https://graphql.anilist.co"
_client = get_client()


@register_tool("anilist_search_anime_by_title")
async def search_anime_by_title(keyword: str) -> dict[str, Any]:
    """
    Get detailed information of the anime by title with AniList API
    The API is only capable of searching with English and Japanese, searching with Chinese is not guaranteed

    Args:
        keyword: The title keyword of the anime

    Results:
        Anime data in JSON format
    """
    query = """
query SearchQuery($search: String) {
  Page(page: 0, perPage: 1) {
    media(type: ANIME, search: $search) {
      title {
        native
        english
      }
      description
      format
      episodes
      season
      seasonYear
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      synonyms
      genres
      tags {
        name
      }
    }
  }
}
"""
    variables = {
        "search": keyword,
    }
    payload = {
        "query": query,
        "variables": variables,
    }

    response = await _client.post(
        ANILIST_API,
        json=payload,
    )
    if not (response.is_success and response.status_code == 200):
        return {}

    return response.json()
