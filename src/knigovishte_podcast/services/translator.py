from __future__ import annotations

from abc import ABC, abstractmethod
import requests

from ..config import TranslationConfig
from ..models import Article, Translation


class ArticleTranslator(ABC):
    @abstractmethod
    def translate(self, article: Article) -> Translation:
        raise NotImplementedError


class PlaceholderTranslator(ArticleTranslator):
    def translate(self, article: Article) -> Translation:
        raise NotImplementedError(
            "Translation is not implemented yet. Add the chosen provider behind this interface."
        )


class LangblyTranslator(ArticleTranslator):
    """Translate articles using Langbly's Google Translate v2 compatible API."""

    def __init__(self, config: TranslationConfig) -> None:
        self.config = config

    def translate(self, article: Article) -> Translation:
        """Translate article title and sentences from Bulgarian to English."""
        # Prepare batch: title + all sentences
        texts_to_translate = [article.title_bg] + list(article.sentences_bg)
        
        # Call Langbly API
        translated_texts = self._translate_batch(texts_to_translate)
        
        # Split result back into title and sentences
        title_en = translated_texts[0]
        sentences_en = tuple(translated_texts[1:])
        
        return Translation(title_en=title_en, sentences_en=sentences_en)

    def _translate_batch(self, texts: list[str]) -> list[str]:
        """Translate a batch of texts via Langbly API."""
        url = f"{self.config.base_url}/language/translate/v2"
        
        payload = {
            "q": texts,
            "source": self.config.source_lang,
            "target": self.config.target_lang,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        try:
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Langbly API error: {response.status_code} {response.text}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Langbly API: {e}") from e
        
        # Parse response: Langbly returns { "data": { "translations": [...] } }
        try:
            data = response.json()
            translations = data.get("data", {}).get("translations", [])
            if not translations:
                raise ValueError("No translations in response")
            # Extract translatedText from each translation object
            translated_texts = [t["translatedText"] for t in translations]
            return translated_texts
        except (KeyError, ValueError, TypeError) as e:
            raise RuntimeError(
                f"Failed to parse Langbly API response: {response.text}"
            ) from e
