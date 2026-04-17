from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from ..models import Article
from .fetcher import KnigovishteArticleFetcher


@dataclass(frozen=True)
class ArticleFilter:
    """Filter criteria for selecting articles from Knigovishte."""

    min_length: int | None = None
    max_length: int | None = None
    category: str | None = None

    @classmethod
    def from_json(cls, json_path: Path) -> "ArticleFilter":
        """Load filter from JSON file."""
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            category=data.get("category"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArticleFilter":
        """Create filter from dictionary."""
        return cls(
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            category=data.get("category"),
        )

    def matches(self, article: Article) -> bool:
        """Check if article matches this filter."""
        sentence_count = len(article.sentences_bg)

        if self.min_length is not None and sentence_count < self.min_length:
            return False

        if self.max_length is not None and sentence_count > self.max_length:
            return False

        # Category matching would require additional article metadata
        # For now, we only filter by length
        return True


@dataclass(frozen=True)
class ArticleListItem:
    """Metadata about an article from the listing page."""

    url: str
    title: str


class KnigovishteListingParser(HTMLParser):
    """Parse article listing pages to extract article links."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.articles: list[ArticleListItem] = []
        self._current_link: str | None = None
        self._current_title_parts: list[str] = []
        self._inside_article_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            attr_map = {name: value or "" for name, value in attrs}
            href = attr_map.get("href", "")
            if re.match(r"^/vijte/\d+-", href):
                self._current_link = href
                self._inside_article_link = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._inside_article_link:
            if self._current_link:
                title = "".join(self._current_title_parts).strip()
                if title:
                    full_url = f"https://www.knigovishte.bg{self._current_link}"
                    self.articles.append(ArticleListItem(url=full_url, title=title))
            self._current_link = None
            self._current_title_parts = []
            self._inside_article_link = False

    def handle_data(self, data: str) -> None:
        if self._inside_article_link:
            self._current_title_parts.append(data)


class ArticleSelector:
    """Select articles from Knigovishte based on filters."""

    def __init__(
        self,
        fetcher: KnigovishteArticleFetcher | None = None,
        *,
        timeout: float = 20.0,
    ) -> None:
        self.fetcher = fetcher or KnigovishteArticleFetcher()
        self.timeout = timeout

    def select_article(
        self,
        article_filter: ArticleFilter | None = None,
        *,
        max_scan: int = 20,
    ) -> Article:
        """
        Select an article from Knigovishte based on filter criteria.

        If no filter is provided, returns the latest article.
        Scans up to max_scan articles from the listing page.
        """
        listing_url = "https://www.knigovishte.bg/vijte"
        article_items = self._fetch_article_list(listing_url)

        if not article_items:
            raise ValueError("No articles found on the Knigovishte listing page.")

        # If no filter, return the first (latest) article
        if article_filter is None:
            return self.fetcher.fetch(article_items[0].url)

        # Scan articles until we find one that matches
        scanned = 0
        for item in article_items:
            if scanned >= max_scan:
                break

            try:
                article = self.fetcher.fetch(item.url)
                if article_filter.matches(article):
                    return article
                scanned += 1
            except Exception:
                # Skip articles that fail to fetch or parse
                scanned += 1
                continue

        raise ValueError(
            f"No article matching the filter criteria found in the first {scanned} articles."
        )

    def _fetch_article_list(self, listing_url: str) -> list[ArticleListItem]:
        """Fetch the article listing page and extract article links."""
        request = Request(
            listing_url,
            headers={
                "User-Agent": "knigovishte-podcast/0.1",
                "Accept-Language": "bg,en;q=0.8",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read().decode(charset, errors="replace")

        parser = KnigovishteListingParser()
        parser.feed(html)
        parser.close()
        return parser.articles
