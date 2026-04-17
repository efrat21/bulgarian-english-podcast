from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from knigovishte_podcast.services.tts import Pyttsx3PodcastAudioGenerator


class PodcastAudioGeneratorTests(unittest.TestCase):
    def test_generate_returns_expected_path_and_invokes_engine(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()
            audio_path = project_root / "audio" / "episode-slug.wav"

            def run_and_wait_side_effect() -> None:
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"dummy audio")

            mock_engine.runAndWait.side_effect = run_and_wait_side_effect

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch("knigovishte_podcast.services.tts.pyttsx3.init", return_value=mock_engine) as mock_init:
                    generator = Pyttsx3PodcastAudioGenerator(rate=150, volume=0.8)
                    result_path = generator.generate("Hello world", "episode-slug")

            self.assertEqual(result_path, audio_path)
            mock_init.assert_called_once()
            mock_engine.save_to_file.assert_called_once_with("Hello world", str(audio_path))
            mock_engine.runAndWait.assert_called_once()

    def test_generate_raises_on_empty_script_text(self) -> None:
        generator = Pyttsx3PodcastAudioGenerator()
        with self.assertRaises(ValueError):
            generator.generate("   ", "episode-slug")

    def test_generate_raises_on_empty_episode_slug(self) -> None:
        generator = Pyttsx3PodcastAudioGenerator()
        with self.assertRaises(ValueError):
            generator.generate("Hello world", "  ")

    def test_generate_sets_requested_voice_when_available(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()
            mock_engine.getProperty.return_value = [
                SimpleNamespace(id="voice-1", name="English Voice"),
            ]
            audio_path = project_root / "audio" / "episode-slug.wav"

            def run_and_wait_side_effect() -> None:
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"dummy audio")

            mock_engine.runAndWait.side_effect = run_and_wait_side_effect

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch("knigovishte_podcast.services.tts.pyttsx3.init", return_value=mock_engine):
                    generator = Pyttsx3PodcastAudioGenerator(voice_name="english")
                    generator.generate("Hello world", "episode-slug")

            mock_engine.setProperty.assert_any_call("voice", "voice-1")

    def test_generate_raises_when_requested_voice_is_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()
            mock_engine.getProperty.return_value = [
                SimpleNamespace(id="voice-1", name="English Voice"),
            ]

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch("knigovishte_podcast.services.tts.pyttsx3.init", return_value=mock_engine):
                    generator = Pyttsx3PodcastAudioGenerator(voice_name="bulgarian")
                    with self.assertRaisesRegex(ValueError, "Requested voice not available"):
                        generator.generate("Hello world", "episode-slug")

    def test_generate_raises_when_voice_name_is_blank(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch("knigovishte_podcast.services.tts.pyttsx3.init", return_value=mock_engine):
                    generator = Pyttsx3PodcastAudioGenerator(voice_name="   ")
                    with self.assertRaisesRegex(ValueError, "voice_name must not be blank"):
                        generator.generate("Hello world", "episode-slug")

    def test_generate_raises_when_audio_file_is_not_created(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()
            audio_path = project_root / "audio" / "episode-slug.wav"
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            audio_path.write_bytes(b"stale audio")

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch("knigovishte_podcast.services.tts.pyttsx3.init", return_value=mock_engine):
                    generator = Pyttsx3PodcastAudioGenerator()
                    with self.assertRaisesRegex(RuntimeError, "Audio generation failed"):
                        generator.generate("Hello world", "episode-slug")

            self.assertFalse(audio_path.exists())


if __name__ == "__main__":
    unittest.main()
