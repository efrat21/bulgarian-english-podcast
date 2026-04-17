from __future__ import annotations

import io
import shutil
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from knigovishte_podcast.cli import main
from knigovishte_podcast.config import ProjectPaths, episode_slug_from_url
from knigovishte_podcast.models import Article, PodcastPlan, Translation
from knigovishte_podcast.pipeline import ArticleToPodcastPipeline


class StubFetcher:
    def __init__(self, article: Article, html: str) -> None:
        self.article = article
        self.html = html
        self.fetch_html_calls = 0
        self.parse_html_calls = 0

    def fetch_html(self, url: str) -> str:
        self.fetch_html_calls += 1
        return self.html

    def parse_html(self, url: str, html: str) -> Article:
        self.parse_html_calls += 1
        return self.article


class StubTranslator:
    def __init__(self, translation: Translation) -> None:
        self.translation = translation
        self.calls: list[Article] = []

    def translate(self, article: Article) -> Translation:
        self.calls.append(article)
        return self.translation


class StubScriptBuilder:
    def __init__(self, script_text: str) -> None:
        self.script_text = script_text
        self.calls: list[tuple[Article, Translation]] = []

    def build(self, article: Article, translation: Translation) -> str:
        self.calls.append((article, translation))
        return self.script_text


class StubAudioGenerator:
    def __init__(self, audio_root: Path) -> None:
        self.audio_root = audio_root
        self.calls: list[tuple[str, str]] = []

    def generate(self, script_text: str, episode_slug: str) -> Path:
        self.calls.append((script_text, episode_slug))
        self.audio_root.mkdir(parents=True, exist_ok=True)
        audio_path = self.audio_root / f"{episode_slug}.wav"
        audio_path.write_bytes(b"audio")
        return audio_path


class ArticleToPodcastPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = Path(__file__).resolve().parent / "_artifacts" / self._testMethodName
        if self.workdir.exists():
            shutil.rmtree(self.workdir)
        self.paths = ProjectPaths.from_root(self.workdir)
        self.paths.ensure()

        self.article = Article(
            source_url="https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha",
            title_bg="Колко тежи една лека муха?",
            sentences_bg=("Първо изречение.",),
        )
        self.translation = Translation(
            title_en="How heavy is a light fly?",
            sentences_en=("First sentence.",),
        )
        self.script_text = "English: First sentence.\nBulgarian: Първо изречение."

    def tearDown(self) -> None:
        if self.workdir.exists():
            shutil.rmtree(self.workdir)

    def test_run_wires_services_and_persists_artifacts(self) -> None:
        fetcher = StubFetcher(self.article, "<html>cached article</html>")
        translator = StubTranslator(self.translation)
        script_builder = StubScriptBuilder(self.script_text)
        audio_generator = StubAudioGenerator(self.paths.audio)
        sut = ArticleToPodcastPipeline(
            fetcher=fetcher,
            translator=translator,
            script_builder=script_builder,
            audio_generator=audio_generator,
            paths=self.paths,
        )

        plan = sut.run(self.article.source_url)

        expected_slug = episode_slug_from_url(self.article.source_url)
        expected_html_path = self.paths.articles / f"{expected_slug}.html"
        expected_script_path = self.paths.scripts / f"{expected_slug}.txt"
        expected_audio_path = self.paths.audio / f"{expected_slug}.wav"

        self.assertEqual(fetcher.fetch_html_calls, 1)
        self.assertEqual(fetcher.parse_html_calls, 1)
        self.assertEqual(translator.calls, [self.article])
        self.assertEqual(script_builder.calls, [(self.article, self.translation)])
        self.assertEqual(audio_generator.calls, [(self.script_text, expected_slug)])
        self.assertEqual(plan.article_html_path, expected_html_path)
        self.assertEqual(plan.script_path, expected_script_path)
        self.assertEqual(plan.audio_path, expected_audio_path)
        self.assertEqual(expected_html_path.read_text(encoding="utf-8"), "<html>cached article</html>")
        self.assertEqual(expected_script_path.read_text(encoding="utf-8"), self.script_text)

    def test_run_reuses_cached_html_on_repeat_runs(self) -> None:
        fetcher = StubFetcher(self.article, "<html>cached article</html>")
        sut = ArticleToPodcastPipeline(
            fetcher=fetcher,
            translator=StubTranslator(self.translation),
            script_builder=StubScriptBuilder(self.script_text),
            audio_generator=StubAudioGenerator(self.paths.audio),
            paths=self.paths,
        )

        sut.run(self.article.source_url)
        sut.run(self.article.source_url)

        self.assertEqual(fetcher.fetch_html_calls, 1)
        self.assertEqual(fetcher.parse_html_calls, 2)


class CliRunCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = Path(__file__).resolve().parent / "_artifacts" / self._testMethodName
        if self.workdir.exists():
            shutil.rmtree(self.workdir)
        self.paths = ProjectPaths.from_root(self.workdir)
        self.paths.ensure()

    def tearDown(self) -> None:
        if self.workdir.exists():
            shutil.rmtree(self.workdir)

    def test_run_command_uses_pipeline_and_reports_artifacts(self) -> None:
        article = Article(
            source_url="https://www.knigovishte.bg/vijte/42-test",
            title_bg="Българско заглавие",
            sentences_bg=("Едно изречение.",),
        )
        translation = Translation(
            title_en="English Title",
            sentences_en=("One sentence.",),
        )
        plan = PodcastPlan(
            article=article,
            translation=translation,
            script_text="script",
            script_path=self.paths.scripts / "vijte-42-test.txt",
            audio_path=self.paths.audio / "vijte-42-test.wav",
            article_html_path=self.paths.articles / "vijte-42-test.html",
        )
        mock_pipeline = Mock()
        mock_pipeline.run.return_value = plan

        stdout = io.StringIO()
        with patch("knigovishte_podcast.cli.ProjectPaths.from_root", return_value=self.paths):
            with patch("knigovishte_podcast.cli.build_pipeline", return_value=mock_pipeline) as build_pipeline_mock:
                with redirect_stdout(stdout):
                    exit_code = main(["run", "--url", article.source_url])

        self.assertEqual(exit_code, 0)
        build_pipeline_mock.assert_called_once_with(paths=self.paths, use_cached_html=True)
        mock_pipeline.run.assert_called_once_with(article.source_url)
        output = stdout.getvalue()
        self.assertIn("Fetched title: Българско заглавие", output)
        self.assertIn("Translated title: English Title", output)
        self.assertIn(f"Script output: {plan.script_path}", output)
        self.assertIn(f"Audio output: {plan.audio_path}", output)


if __name__ == "__main__":
    unittest.main()
