from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pyttsx3

from ..config import ProjectPaths


class PodcastAudioGenerator(ABC):
    @abstractmethod
    def generate(self, script_text: str, episode_slug: str) -> Path:
        raise NotImplementedError


class PlaceholderPodcastAudioGenerator(PodcastAudioGenerator):
    def generate(self, script_text: str, episode_slug: str) -> Path:
        raise NotImplementedError(
            "Audio generation is not implemented yet. Add the selected TTS engine behind this interface."
        )


class Pyttsx3PodcastAudioGenerator(PodcastAudioGenerator):
    """Generate podcast audio locally using pyttsx3."""

    def __init__(
        self,
        voice_name: str | None = None,
        rate: int | None = None,
        volume: float | None = None,
    ) -> None:
        self.voice_name = voice_name
        self.rate = rate
        self.volume = volume

    def generate(self, script_text: str, episode_slug: str) -> Path:
        if not script_text or not script_text.strip():
            raise ValueError("script_text must not be empty.")
        if not episode_slug or not episode_slug.strip():
            raise ValueError("episode_slug must not be empty.")

        project_paths = ProjectPaths.from_root()
        project_paths.ensure()

        audio_path = project_paths.audio / f"{episode_slug}.wav"
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        engine = pyttsx3.init()
        try:
            if self.rate is not None:
                engine.setProperty("rate", self.rate)
            if self.volume is not None:
                engine.setProperty("volume", self.volume)
            if self.voice_name is not None:
                voices = engine.getProperty("voices") or []
                for voice in voices:
                    if self.voice_name.lower() in voice.name.lower():
                        engine.setProperty("voice", voice.id)
                        break

            engine.save_to_file(script_text, str(audio_path))
            engine.runAndWait()
        finally:
            engine.stop()

        if not audio_path.exists():
            raise RuntimeError(
                f"Audio generation failed; file was not created: {audio_path}"
            )

        return audio_path
