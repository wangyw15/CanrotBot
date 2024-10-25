from typing import TypedDict


class SearchInfo(TypedDict):
    totalhits: int


class Search(TypedDict):
    ns: int
    title: str
    pageid: int
    size: int
    wordcount: int
    snippet: str
    timestamp: str


class Query(TypedDict):
    searchinfo: SearchInfo
    search: list[Search]


class Response(TypedDict):
    batchcomplete: bool
    query: Query


__all__ = [
    "SearchInfo",
    "Search",
    "Query",
    "Response",
]
