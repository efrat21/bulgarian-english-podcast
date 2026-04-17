#!/usr/bin/env python
"""
Test Langbly API key with a real translation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from knigovishte_podcast.config import TranslationConfig
from knigovishte_podcast.models import Article
from knigovishte_podcast.services.translator import LangblyTranslator


def test_real_api():
    """Test with real Langbly API."""
    print("🔑 Testing Langbly API Key")
    print("-" * 60)

    # Test article in Bulgarian
    article = Article(
        source_url="https://test.com",
        title_bg="Здравей свят",
        sentences_bg=("Това е тест.", "Преводът работи ли?"),
    )

    print("📄 Test Article:")
    print(f"   Title: {article.title_bg}")
    print(f"   Sentences: {len(article.sentences_bg)}")
    for i, sent in enumerate(article.sentences_bg, 1):
        print(f"   {i}. {sent}")

    # Load config
    try:
        config = TranslationConfig.from_env()
        print(f"\n✅ Config loaded: {config.base_url}")
    except ValueError as e:
        print(f"\n❌ Config error: {e}")
        print("\n📝 To fix this:")
        print("1. Create a file named '.env' in this directory")
        print("2. Add your Langbly API key:")
        print("   LANGBLY_API_KEY=your_actual_api_key_here")
        print("3. Optional: LANGBLY_BASE_URL=https://api.langbly.com")
        print("\n💡 The .env file is already in .gitignore, so it's safe!")
        return 1

    # Test translation
    print(f"\n🌐 Calling Langbly API...")
    try:
        translator = LangblyTranslator(config)
        translation = translator.translate(article)

        print("✅ Translation successful!")
        print(f"\n📄 English Translation:")
        print(f"   Title: {translation.title_en}")
        for i, sent in enumerate(translation.sentences_en, 1):
            print(f"   {i}. {sent}")

        return 0

    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(test_real_api())
