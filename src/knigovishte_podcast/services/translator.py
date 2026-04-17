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
        texts_to_translate = [article.title_bg] + list(article.sentences_bg)
        translated_texts = self._translate_batch(texts_to_translate)
        title_en = translated_texts[0]
        sentences_en = tuple(translated_texts[1:])

        return Translation(title_en=title_en, sentences_en=sentences_en)

    def _translate_batch(self, texts: list[str]) -> list[str]:
        """Translate a batch of texts via Langbly API."""
        if not texts:
            return []

        url = f"{self.config.base_url.rstrip('/')}/language/translate/v2"
        payload = {
            "q": texts,
            "source": self.config.source_lang,
            "target": self.config.target_lang,
            "key": self.config.api_key,
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        response: requests.Response | None = None

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response or response
            status_code = getattr(error_response, "status_code", "unknown")
            response_text = getattr(error_response, "text", "")
            raise RuntimeError(
                f"Langbly API error: {status_code} {response_text}".strip()
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Failed to connect to Langbly API: {exc}") from exc

        try:
            data = response.json()
            translations = data.get("data", {}).get("translations")
            if not isinstance(translations, list) or len(translations) != len(texts):
                raise ValueError("Unexpected translation count in response")

            translated_texts: list[str] = []
            for translation in translations:
                translated_text = translation.get("translatedText")
                if not isinstance(translated_text, str) or not translated_text.strip():
                    raise ValueError("Missing translatedText in response")
                translated_texts.append(translated_text.strip())
            return translated_texts
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to parse Langbly API response: {response.text}"
            ) from exc
