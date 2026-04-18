from __future__ import annotations

import wave
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pyttsx3

from ..config import GoogleTTSConfig, ProjectPaths

AUDIO_FILE_EXTENSION = ".wav"
DEFAULT_BG_GOOGLE_VOICE = "bg-BG-Standard-B"

_BG_LINE_PREFIXES = ("Bulgarian:", "Bulgarian title:")

_google_texttospeech: Any | None
try:
    from google.cloud import texttospeech as _google_texttospeech
except ImportError:
    _google_texttospeech = None

google_texttospeech: Any | None = _google_texttospeech


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
    """Generate podcast audio with local English TTS and optional Google Bulgarian TTS."""

    def __init__(
        self,
        voice_name: str | None = None,
        rate: int | None = None,
        volume: float | None = None,
        bg_voice_name: str | None = None,
        google_tts_config: GoogleTTSConfig | None = None,
        google_client: Any | None = None,
    ) -> None:
        self.voice_name = voice_name
        self.rate = rate
        self.volume = volume
        self.bg_voice_name = bg_voice_name
        self.google_tts_config = google_tts_config or GoogleTTSConfig.from_env()
        self._google_client = google_client

    def generate(self, script_text: str, episode_slug: str) -> Path:
        if not script_text or not script_text.strip():
            raise ValueError("script_text must not be empty.")
        if not episode_slug or not episode_slug.strip():
            raise ValueError("episode_slug must not be empty.")

        normalized_slug = episode_slug.strip()

        project_paths = ProjectPaths.from_root()
        project_paths.ensure()

        audio_path = project_paths.audio / f"{normalized_slug}{AUDIO_FILE_EXTENSION}"
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        if audio_path.exists():
            audio_path.unlink()

        if self.bg_voice_name is not None:
            self._generate_bilingual(script_text, audio_path)
        else:
            self._generate_single_voice(script_text, audio_path)

        if not audio_path.exists():
            raise RuntimeError(
                f"Audio generation failed; file was not created: {audio_path}"
            )

        return audio_path

    def _generate_single_voice(self, script_text: str, audio_path: Path) -> None:
        self._synthesize_local_segment(script_text, audio_path, self.voice_name)

    def _synthesize_local_segment(
        self,
        text: str,
        audio_path: Path,
        voice_name: str | None,
    ) -> None:
        engine = pyttsx3.init()
        try:
            if self.rate is not None:
                engine.setProperty("rate", self.rate)
            if self.volume is not None:
                engine.setProperty("volume", self.volume)
            if voice_name is not None:
                self._set_voice(engine, voice_name)

            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
        finally:
            engine.stop()

    def _generate_bilingual(self, script_text: str, audio_path: Path) -> None:
        segments = _split_script_by_language(script_text)
        temp_files: list[Path] = []
        try:
            for i, (lang, text) in enumerate(segments):
                temp_path = audio_path.parent / f"_{audio_path.stem}_part{i}{AUDIO_FILE_EXTENSION}"
                if lang == "bg" and _is_google_bg_voice(self.bg_voice_name):
                    self._synthesize_google_segment(text, temp_path)
                else:
                    voice_name = self.bg_voice_name if lang == "bg" else self.voice_name
                    self._synthesize_local_segment(text, temp_path, voice_name)
                temp_files.append(temp_path)
            _concatenate_wav_files(temp_files, audio_path)
        finally:
            for tf in temp_files:
                tf.unlink(missing_ok=True)

    def _set_voice(self, engine: pyttsx3.Engine, voice_name: str) -> None:
        requested_voice = voice_name.strip().lower()
        if not requested_voice:
            raise ValueError("voice_name must not be blank when provided.")

        voices = engine.getProperty("voices") or []
        for voice in voices:
            v_name = getattr(voice, "name", "") or ""
            v_id = getattr(voice, "id", "") or ""
            if requested_voice in v_name.lower() or requested_voice in v_id.lower():
                engine.setProperty("voice", v_id)
                return

        raise ValueError(f"Requested voice not available: {voice_name}")

    def _synthesize_google_segment(self, text: str, output_path: Path) -> None:
        voice_name = (self.bg_voice_name or "").strip()
        if not voice_name:
            raise ValueError("bg_voice_name must not be blank when provided.")
        google_api = google_texttospeech
        if google_api is None:
            raise RuntimeError(
                "Google Cloud Text-to-Speech is unavailable. Install google-cloud-texttospeech "
                "and configure GOOGLE_APPLICATION_CREDENTIALS to render Bulgarian audio."
            )

        client = self._get_google_client()
        response = client.synthesize_speech(
            input=google_api.SynthesisInput(text=text),
            voice=google_api.VoiceSelectionParams(
                language_code=self.google_tts_config.bg_language_code,
                name=voice_name,
            ),
            audio_config=google_api.AudioConfig(
                audio_encoding=google_api.AudioEncoding.LINEAR16
            ),
        )
        audio_content = getattr(response, "audio_content", b"")
        if not audio_content:
            raise RuntimeError("Google Cloud TTS returned empty audio content.")
        output_path.write_bytes(audio_content)

    def _get_google_client(self) -> Any:
        google_api = google_texttospeech
        if google_api is None:
            raise RuntimeError(
                "Google Cloud Text-to-Speech is unavailable. Install google-cloud-texttospeech "
                "and configure GOOGLE_APPLICATION_CREDENTIALS to render Bulgarian audio."
            )
        if self._google_client is None:
            try:
                self._google_client = google_api.TextToSpeechClient()
            except Exception as exc:
                raise RuntimeError(
                    "Google Cloud Text-to-Speech is not configured for Bulgarian audio. "
                    "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file."
                ) from exc
        return self._google_client


def build_default_audio_generator(
    *,
    voice_name: str | None = None,
    bg_voice_name: str | None = None,
    rate: int | None = None,
    volume: float | None = None,
) -> Pyttsx3PodcastAudioGenerator:
    google_tts_config = GoogleTTSConfig.from_env()
    return Pyttsx3PodcastAudioGenerator(
        voice_name=voice_name,
        rate=rate,
        volume=volume,
        bg_voice_name=bg_voice_name or google_tts_config.bg_voice_name,
        google_tts_config=google_tts_config,
    )


def _split_script_by_language(script_text: str) -> list[tuple[str, str]]:
    """Split a podcast script into (language, text) segments.

    Lines whose text starts with a Bulgarian prefix are tagged ``'bg'``;
    all other lines (including blank separator lines) are tagged ``'en'``.
    Consecutive lines with the same tag are merged into a single segment.
    """
    segments: list[tuple[str, str]] = []
    current_lang: str = "en"
    current_lines: list[str] = []

    for line in script_text.splitlines():
        lang = "bg" if any(line.startswith(p) for p in _BG_LINE_PREFIXES) else "en"
        if lang != current_lang:
            if current_lines:
                segments.append((current_lang, "\n".join(current_lines)))
            current_lang = lang
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        segments.append((current_lang, "\n".join(current_lines)))

    return segments


def _is_google_bg_voice(voice_name: str | None) -> bool:
    return bool(voice_name and voice_name.strip().lower().startswith("bg-bg-"))


def _concatenate_wav_files(input_paths: list[Path], output_path: Path) -> None:
    """Concatenate multiple WAV files into a single output WAV file."""
    existing = [p for p in input_paths if p.exists()]
    if not existing:
        return

    with wave.open(str(output_path), "wb") as out_wav:
        for i, path in enumerate(existing):
            with wave.open(str(path), "rb") as in_wav:
                if i == 0:
                    out_wav.setparams(in_wav.getparams())
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
