from __future__ import annotations

from collections.abc import Iterable

from .config import DOUYIN_HOST_KEYWORDS, TRAILING_URL_CHARS, URL_PATTERN


class LinkProcessor:
    def __init__(self, only_douyin: bool = False) -> None:
        self.only_douyin = only_douyin

    def extract_links(self, text: str) -> list[str]:
        raw_links = URL_PATTERN.findall(text)
        cleaned_links: list[str] = []

        for link in raw_links:
            normalized = self.normalize_url(link)
            if not normalized:
                continue
            if self.only_douyin and not self.is_douyin_url(normalized):
                continue
            cleaned_links.append(normalized)

        return cleaned_links

    def normalize_url(self, url: str) -> str:
        return url.strip().rstrip(TRAILING_URL_CHARS)

    def deduplicate(self, links: Iterable[str]) -> list[str]:
        seen = set()
        result = []

        for link in links:
            if link in seen:
                continue
            seen.add(link)
            result.append(link)

        return result

    def is_douyin_url(self, url: str) -> bool:
        lower_url = url.lower()
        return any(keyword in lower_url for keyword in DOUYIN_HOST_KEYWORDS)
