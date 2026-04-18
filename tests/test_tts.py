from __future__ import annotations

import io
import sys
import unittest
import wave
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from knigovishte_podcast.config import GoogleTTSConfig
from knigovishte_podcast.services.tts import (
    DEFAULT_BG_GOOGLE_VOICE,
    Pyttsx3PodcastAudioGenerator,
    _concatenate_wav_files,
    _split_script_by_language,
    build_default_audio_generator,
)


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


class SplitScriptByLanguageTests(unittest.TestCase):
    def test_empty_script_returns_empty_list(self) -> None:
        self.assertEqual(_split_script_by_language(""), [])

    def test_all_english_lines_produce_single_en_segment(self) -> None:
        script = "Welcome.\nEnglish title: Foo\nEnglish: Hello."
        segments = _split_script_by_language(script)
        self.assertEqual(len(segments), 1)
        lang, text = segments[0]
        self.assertEqual(lang, "en")
        self.assertIn("Welcome.", text)

    def test_bulgarian_line_creates_bg_segment(self) -> None:
        script = "English: Hello.\nBulgarian: Здравей."
        segments = _split_script_by_language(script)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0][0], "en")
        self.assertEqual(segments[1][0], "bg")
        self.assertIn("Здравей.", segments[1][1])

    def test_bulgarian_title_line_creates_bg_segment(self) -> None:
        script = "English title: Foo\nBulgarian title: Бар\nEnglish: Hi."
        segments = _split_script_by_language(script)
        self.assertEqual(segments[0][0], "en")
        self.assertEqual(segments[1][0], "bg")
        self.assertEqual(segments[2][0], "en")

    def test_consecutive_lines_same_lang_are_merged(self) -> None:
        script = "English: Hello.\nEnglish title: Foo\nBulgarian: Здравей.\nBulgarian title: Бар"
        segments = _split_script_by_language(script)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0][0], "en")
        self.assertEqual(segments[1][0], "bg")


class ConcatenateWavFilesTests(unittest.TestCase):
    def _make_wav(self, path: Path, num_frames: int = 4) -> None:
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            w.writeframes(b"\x00\x00" * num_frames)

    def test_concatenation_produces_combined_frames(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            part0 = root / "part0.wav"
            part1 = root / "part1.wav"
            output = root / "out.wav"

            self._make_wav(part0, num_frames=4)
            self._make_wav(part1, num_frames=6)

            _concatenate_wav_files([part0, part1], output)

            self.assertTrue(output.exists())
            with wave.open(str(output), "rb") as w:
                self.assertEqual(w.getnframes(), 10)

    def test_missing_input_files_are_skipped(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            present = root / "present.wav"
            missing = root / "missing.wav"
            output = root / "out.wav"

            self._make_wav(present, num_frames=3)

            _concatenate_wav_files([missing, present], output)

            self.assertTrue(output.exists())
            with wave.open(str(output), "rb") as w:
                self.assertEqual(w.getnframes(), 3)

    def test_no_existing_files_produces_no_output(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output = root / "out.wav"
            _concatenate_wav_files([root / "ghost.wav"], output)
            self.assertFalse(output.exists())


class BilingualAudioGeneratorTests(unittest.TestCase):
    def _make_dummy_engine(self, audio_path: Path) -> Mock:
        """Return a mock pyttsx3 engine whose runAndWait writes a minimal WAV."""

        def _run_and_wait() -> None:
            # save_to_file(text, path) → positional args[1] is the destination path
            dest = Path(mock_engine.save_to_file.call_args.args[1])
            dest.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(dest), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(22050)
                w.writeframes(b"\x00\x00" * 4)

        mock_engine = Mock()
        mock_engine.getProperty.return_value = [
            SimpleNamespace(id="en-voice-id", name="English Voice"),
            SimpleNamespace(id="bg-voice-id", name="Bulgarian Voice"),
        ]
        mock_engine.runAndWait.side_effect = _run_and_wait
        return mock_engine

    def _make_wav_bytes(self, num_frames: int = 4) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            w.writeframes(b"\x00\x00" * num_frames)
        return buffer.getvalue()

    def test_bilingual_generate_uses_bg_voice_for_bulgarian_lines(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            audio_path = project_root / "audio" / "ep.wav"
            mock_engine = self._make_dummy_engine(audio_path)

            script = "English: Hello.\nBulgarian: Здравей."

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch(
                    "knigovishte_podcast.services.tts.pyttsx3.init",
                    return_value=mock_engine,
                ):
                    generator = Pyttsx3PodcastAudioGenerator(
                        voice_name="english",
                        bg_voice_name="bulgarian",
                    )
                    result = generator.generate(script, "ep")

            self.assertTrue(result.exists())
            set_voice_calls = [
                c for c in mock_engine.setProperty.call_args_list if c[0][0] == "voice"
            ]
            voice_ids_used = [c[0][1] for c in set_voice_calls]
            self.assertIn("en-voice-id", voice_ids_used)
            self.assertIn("bg-voice-id", voice_ids_used)

    def test_bilingual_generate_temp_files_are_cleaned_up(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            audio_path = project_root / "audio" / "ep.wav"
            mock_engine = self._make_dummy_engine(audio_path)

            script = "English: Hello.\nBulgarian: Здравей."

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch(
                    "knigovishte_podcast.services.tts.pyttsx3.init",
                    return_value=mock_engine,
                ):
                    generator = Pyttsx3PodcastAudioGenerator(
                        voice_name="english",
                        bg_voice_name="bulgarian",
                    )
                    generator.generate(script, "ep")

            # Temporary part files must be removed after generation.
            temp_files = list((project_root / "audio").glob("_ep_part*.wav"))
            self.assertEqual(temp_files, [])

    def test_bilingual_raises_when_bg_voice_not_found(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            mock_engine = Mock()
            mock_engine.getProperty.return_value = [
                SimpleNamespace(id="en-voice-id", name="English Voice"),
            ]

            script = "English: Hello.\nBulgarian: Здравей."

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch(
                    "knigovishte_podcast.services.tts.pyttsx3.init",
                    return_value=mock_engine,
                ):
                    generator = Pyttsx3PodcastAudioGenerator(
                        voice_name="english",
                        bg_voice_name="bulgarian",
                    )
                    with self.assertRaisesRegex(ValueError, "Requested voice not available"):
                        generator.generate(script, "ep")

    def test_bilingual_google_bg_voice_uses_google_client(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            class DummyPaths:
                root = project_root
                audio = project_root / "audio"

                def ensure(self) -> None:
                    self.audio.mkdir(parents=True, exist_ok=True)

            audio_path = project_root / "audio" / "ep.wav"
            mock_engine = self._make_dummy_engine(audio_path)
            google_client = Mock()
            google_client.synthesize_speech.return_value = SimpleNamespace(
                audio_content=self._make_wav_bytes()
            )
            fake_google = SimpleNamespace(
                SynthesisInput=lambda *, text: {"text": text},
                VoiceSelectionParams=lambda **kwargs: kwargs,
                AudioConfig=lambda **kwargs: kwargs,
                AudioEncoding=SimpleNamespace(LINEAR16="LINEAR16"),
            )

            script = "English: Hello.\nBulgarian: Здравей."

            with patch(
                "knigovishte_podcast.services.tts.ProjectPaths.from_root",
                return_value=DummyPaths(),
            ):
                with patch(
                    "knigovishte_podcast.services.tts.pyttsx3.init",
                    return_value=mock_engine,
                ):
                    with patch(
                        "knigovishte_podcast.services.tts.google_texttospeech",
                        fake_google,
                    ):
                        generator = Pyttsx3PodcastAudioGenerator(
                            voice_name="english",
                            bg_voice_name=DEFAULT_BG_GOOGLE_VOICE,
                            google_tts_config=GoogleTTSConfig(
                                bg_voice_name=DEFAULT_BG_GOOGLE_VOICE,
                                bg_language_code="bg-BG",
                            ),
                            google_client=google_client,
                        )
                        result = generator.generate(script, "ep")

            self.assertTrue(result.exists())
            google_client.synthesize_speech.assert_called_once()
            set_voice_calls = [
                c for c in mock_engine.setProperty.call_args_list if c[0][0] == "voice"
            ]
            voice_ids_used = [c[0][1] for c in set_voice_calls]
            self.assertIn("en-voice-id", voice_ids_used)
            self.assertNotIn("bg-voice-id", voice_ids_used)


class BuildDefaultAudioGeneratorTests(unittest.TestCase):
    def test_default_factory_uses_google_bulgarian_voice(self) -> None:
        config = GoogleTTSConfig(bg_voice_name=DEFAULT_BG_GOOGLE_VOICE, bg_language_code="bg-BG")
        with patch(
            "knigovishte_podcast.services.tts.GoogleTTSConfig.from_env",
            return_value=config,
        ):
            generator = build_default_audio_generator()

        self.assertEqual(generator.bg_voice_name, DEFAULT_BG_GOOGLE_VOICE)
        self.assertEqual(generator.google_tts_config, config)


if __name__ == "__main__":
    unittest.main()
