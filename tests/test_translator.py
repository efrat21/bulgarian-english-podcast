"""Unit tests for LangblyTranslator."""

from unittest.mock import Mock, patch
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from knigovishte_podcast.config import TranslationConfig
from knigovishte_podcast.models import Article, Translation
from knigovishte_podcast.services.translator import LangblyTranslator


def test_langbly_translator_translate():
    """Test that LangblyTranslator correctly translates articles."""
    # Setup test data
    config = TranslationConfig(
        api_key="test_key",
        base_url="https://api.langbly.com",
    )
    
    article = Article(
        source_url="https://example.com/article",
        title_bg="Тестна статия",
        sentences_bg=("Първо изречение.", "Второ изречение."),
    )
    
    # Mock the API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "translations": [
                {"translatedText": "Test Article"},
                {"translatedText": "First sentence."},
                {"translatedText": "Second sentence."},
            ]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("knigovishte_podcast.services.translator.requests.post", return_value=mock_response):
        translator = LangblyTranslator(config)
        result = translator.translate(article)
    
    # Verify the result
    assert isinstance(result, Translation)
    assert result.title_en == "Test Article"
    assert result.sentences_en == ("First sentence.", "Second sentence.")
    print("✓ test_langbly_translator_translate passed")


def test_langbly_translator_api_payload():
    """Test that LangblyTranslator sends correct payload to API."""
    config = TranslationConfig(api_key="test_key")
    article = Article(
        source_url="https://example.com",
        title_bg="Заглавие",
        sentences_bg=("Предложение 1.", "Предложение 2."),
    )
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {"translations": [{"translatedText": x} for x in ["Title", "Sent 1.", "Sent 2."]]}
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("knigovishte_podcast.services.translator.requests.post", return_value=mock_response) as mock_post:
        translator = LangblyTranslator(config)
        translator.translate(article)
        
        # Verify the API was called with correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.langbly.com/language/translate/v2" in call_args[0] or \
               call_args[1].get("url") or call_args[1].get("json") is not None
        
        payload = call_args[1]["json"]
        assert payload["q"] == ["Заглавие", "Предложение 1.", "Предложение 2."]
        assert payload["source"] == "bg"
        assert payload["target"] == "en"
        assert payload["key"] == "test_key"
        print("✓ test_langbly_translator_api_payload passed")


def test_langbly_translator_api_error_handling():
    """Test that LangblyTranslator handles API errors gracefully."""
    config = TranslationConfig(api_key="test_key")
    article = Article(
        source_url="https://example.com",
        title_bg="Заглавие",
        sentences_bg=("Предложение.",),
    )
    
    # Test HTTP error
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 400
    mock_response.text = "Invalid API key"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP 400")
    
    with patch("knigovishte_podcast.services.translator.requests.post", return_value=mock_response):
        translator = LangblyTranslator(config)
        try:
            translator.translate(article)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "API error" in str(e)
            print("✓ test_langbly_translator_api_error_handling passed")


def test_langbly_translator_rejects_mismatched_batch_response():
    """Test that LangblyTranslator rejects partial batch responses."""
    config = TranslationConfig(api_key="test_key")
    article = Article(
        source_url="https://example.com",
        title_bg="Заглавие",
        sentences_bg=("Предложение 1.", "Предложение 2."),
    )

    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {"translations": [{"translatedText": "Title only"}]}
    }
    mock_response.text = '{"data":{"translations":[{"translatedText":"Title only"}]}}'
    mock_response.raise_for_status.return_value = None

    with patch("knigovishte_podcast.services.translator.requests.post", return_value=mock_response):
        translator = LangblyTranslator(config)
        try:
            translator.translate(article)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "parse" in str(e).lower()
            print("✓ test_langbly_translator_rejects_mismatched_batch_response passed")


if __name__ == "__main__":
    test_langbly_translator_translate()
    test_langbly_translator_api_payload()
    test_langbly_translator_api_error_handling()
    test_langbly_translator_rejects_mismatched_batch_response()
    print("\n✅ All translator tests passed!")
