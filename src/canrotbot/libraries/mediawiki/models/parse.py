from typing import TypedDict


class Parse(TypedDict):
    title: str
    pageid: int
    wikitext: str


class Response(TypedDict):
    parse: Parse


__all__ = [
    "Parse",
    "Response",
]
