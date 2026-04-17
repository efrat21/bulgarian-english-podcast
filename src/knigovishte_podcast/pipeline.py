from __future__ import annotations

from dataclasses import dataclass

from .config import episode_slug_from_url
from .models import PodcastPlan
from .services.fetcher import ArticleFetcher
from .services.script_builder import PodcastScriptBuilder
from .services.translator import ArticleTranslator
from .services.tts import PodcastAudioGenerator


@dataclass
class ArticleToPodcastPipeline:
    fetcher: ArticleFetcher
    translator: ArticleTranslator
    script_builder: PodcastScriptBuilder
    audio_generator: PodcastAudioGenerator

    def run(self, url: str) -> PodcastPlan:
        article = self.fetcher.fetch(url)
        translation = self.translator.translate(article)
        script_text = self.script_builder.build(article, translation)
        audio_path = self.audio_generator.generate(script_text, episode_slug_from_url(url))
        return PodcastPlan(
            article=article,
            translation=translation,
            script_text=script_text,
            audio_path=audio_path,
        )
