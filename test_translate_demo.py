#!/usr/bin/env python
"""
Demo script showing how to use LangblyTranslator.

To run this:
1. Create a .env file with LANGBLY_API_KEY=your_key
2. python test_translate_demo.py

This will test the translator with a real Bulgarian article URL.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from knigovishte_podcast.config import ProjectPaths, TranslationConfig
from knigovishte_podcast.services.fetcher import KnigovishteArticleFetcher
from knigovishte_podcast.services.translator import LangblyTranslator


def main():
    # Example: must be a knigovishte.bg/vijte/... URL
    test_url = "https://www.knigovishte.bg/vijte/moy_izbor_sto_cheta_angela_boyanova"
    
    print(f"📰 Fetching article from {test_url}")
    print("-" * 60)
    
    paths = ProjectPaths.from_root()
    fetcher = KnigovishteArticleFetcher()
    
    try:
        # Step 1: Fetch and parse the article
        html = fetcher.fetch_html(test_url)
        article = fetcher.parse_html(test_url, html)
        print(f"✓ Fetched article: {article.title_bg}")
        print(f"  Sentences: {len(article.sentences_bg)}")
        if article.sentences_bg:
            print(f"  First sentence: {article.sentences_bg[0][:50]}...")
        
        # Step 2: Load translation config
        print("\n🔑 Loading Langbly API config from .env...")
        try:
            config = TranslationConfig.from_env(paths.root)
            print(f"✓ API key loaded (base_url: {config.base_url})")
        except ValueError as e:
            print(f"✗ Config error: {e}")
            print("\n   Fix: Create .env file with:")
            print("   LANGBLY_API_KEY=your_actual_key")
            return 1
        
        # Step 3: Translate
        print("\n🌐 Translating to English...")
        translator = LangblyTranslator(config)
        translation = translator.translate(article)
        print(f"✓ Translation complete!")
        print(f"  English title: {translation.title_en}")
        if translation.sentences_en:
            print(f"  First translated sentence: {translation.sentences_en[0][:50]}...")
        
        print("\n✅ Translation pipeline works!")
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
