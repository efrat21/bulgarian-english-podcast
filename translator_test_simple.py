#!/usr/bin/env python
"""
Simple translator test without needing the fetcher or real API key.
This tests the LangblyTranslator directly with mock data.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from knigovishte_podcast.config import TranslationConfig
from knigovishte_podcast.models import Article, Translation
from knigovishte_podcast.services.translator import LangblyTranslator


def test_translator_with_mock_api():
    """Test translator with mocked API response."""
    print("🧪 Testing LangblyTranslator with Mocked API")
    print("-" * 60)
    
    # Create test article in Bulgarian
    article = Article(
        source_url="https://www.knigovishte.bg/test",
        title_bg="Тестна статия за преводачот",
        sentences_bg=(
            "Това е първо изречение.",
            "Това е второ изречение.",
            "И трето изречение.",
        ),
    )
    
    print(f"📄 Test Article:")
    print(f"   Title: {article.title_bg}")
    print(f"   Sentences: {len(article.sentences_bg)}")
    
    # Create config
    config = TranslationConfig(api_key="test_key_12345")
    print(f"\n🔑 Config:")
    print(f"   API Key: {config.api_key}")
    print(f"   Base URL: {config.base_url}")
    print(f"   Source: {config.source_lang} → Target: {config.target_lang}")
    
    # Mock the Langbly API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "translations": [
                {"translatedText": "Test article about the translator"},
                {"translatedText": "This is the first sentence."},
                {"translatedText": "This is the second sentence."},
                {"translatedText": "And the third sentence."},
            ]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    print(f"\n🌐 Running translation...")
    with patch("knigovishte_podcast.services.translator.requests.post", return_value=mock_response) as mock_post:
        translator = LangblyTranslator(config)
        translation = translator.translate(article)
        
        # Verify the API call
        assert mock_post.called, "API should have been called"
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        
        print(f"   URL: {call_args[0][0]}")
        print(f"   Payload keys: {list(payload.keys())}")
        print(f"   Source language: {payload['source']}")
        print(f"   Target language: {payload['target']}")
        print(f"   Batch size: {len(payload['q'])} texts")
    
    print(f"\n✓ Translation Result:")
    print(f"   Title: {translation.title_en}")
    for i, sentence in enumerate(translation.sentences_en, 1):
        print(f"   Sentence {i}: {sentence}")
    
    # Verify result structure
    assert isinstance(translation, Translation), "Result should be a Translation object"
    assert len(translation.sentences_en) == 3, "Should have 3 translated sentences"
    
    print(f"\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(test_translator_with_mock_api())
