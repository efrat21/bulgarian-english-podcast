from __future__ import annotations

import argparse

from .config import ProjectPaths, TranslationConfig, episode_slug_from_url
from .services.fetcher import KnigovishteArticleFetcher
from .services.tts import AUDIO_FILE_EXTENSION
from .services.translator import LangblyTranslator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knigovishte-podcast",
        description="Plan local output paths for a Knigovishte article-to-podcast run.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser(
        "plan",
        help="Create local data folders and print the planned output paths for a source URL.",
    )
    plan_parser.add_argument("--url", required=True, help="Knigovishte article URL.")

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch a Knigovishte article, cache its HTML locally, and print the parsed summary.",
    )
    fetch_parser.add_argument("--url", required=True, help="Knigovishte article URL.")

    translate_parser = subparsers.add_parser(
        "translate",
        help="Fetch and translate a Knigovishte article from Bulgarian to English.",
    )
    translate_parser.add_argument("--url", required=True, help="Knigovishte article URL.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "plan":
        paths = ProjectPaths.from_root()
        paths.ensure()
        slug = episode_slug_from_url(args.url)

        print("Stack: Python 3.11+ stdlib-first CLI scaffold")
        print(f"Source URL: {args.url}")
        print(f"Episode slug: {slug}")
        print(f"Article cache: {paths.articles / f'{slug}.html'}")
        print(f"Script output: {paths.scripts / f'{slug}.txt'}")
        print(f"Audio output: {paths.audio / f'{slug}{AUDIO_FILE_EXTENSION}'}")
        return 0

    if args.command == "fetch":
        paths = ProjectPaths.from_root()
        paths.ensure()
        fetcher = KnigovishteArticleFetcher()
        try:
            html = fetcher.fetch_html(args.url)
            article = fetcher.parse_html(args.url, html)
        except Exception as exc:
            print(f"Fetch failed: {exc}")
            return 1

        slug = episode_slug_from_url(article.source_url)
        cache_path = paths.articles / f"{slug}.html"
        cache_path.write_text(html, encoding="utf-8")

        print(f"Fetched title: {article.title_bg}")
        print(f"Article URL: {article.source_url}")
        print(f"Sentence count: {len(article.sentences_bg)}")
        print(f"Cached HTML: {cache_path}")
        if article.sentences_bg:
            print(f"First sentence: {article.sentences_bg[0]}")
        return 0

    if args.command == "translate":
        paths = ProjectPaths.from_root()
        paths.ensure()
        fetcher = KnigovishteArticleFetcher()
        try:
            html = fetcher.fetch_html(args.url)
            article = fetcher.parse_html(args.url, html)
        except Exception as exc:
            print(f"Fetch failed: {exc}")
            return 1

        try:
            config = TranslationConfig.from_env(paths.root)
            translator = LangblyTranslator(config)
            translation = translator.translate(article)
        except Exception as exc:
            print(f"Translation failed: {exc}")
            return 1

        slug = episode_slug_from_url(article.source_url)
        print(f"Translated title: {translation.title_en}")
        print(f"Article URL: {article.source_url}")
        print(f"Translated sentence count: {len(translation.sentences_en)}")
        if translation.sentences_en:
            print(f"First translated sentence: {translation.sentences_en[0]}")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2
