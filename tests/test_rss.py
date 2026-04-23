from __future__ import annotations

import os
import shutil
import sys
import threading
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from knigovishte_podcast.config import ProjectPaths
from knigovishte_podcast.services.rss import LocalRSSService


class LocalRSSServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = Path(__file__).resolve().parent / "_artifacts" / self._testMethodName
        if self.workdir.exists():
            shutil.rmtree(self.workdir)
        self.paths = ProjectPaths.from_root(self.workdir)
        self.paths.ensure()
        self.service = LocalRSSService(self.paths)

    def tearDown(self) -> None:
        if self.workdir.exists():
            shutil.rmtree(self.workdir)

    def test_rebuild_feed_stages_supported_audio_and_cleans_stale_files(self) -> None:
        older_audio = self.paths.audio / "older.mp3"
        older_audio.write_bytes(b"older-audio")
        newest_audio = self.paths.audio / "newest.wav"
        newest_audio.write_bytes(b"newest-audio")
        os.utime(older_audio, (1_700_000_000, 1_700_000_000))
        os.utime(newest_audio, (1_600_000_000, 1_600_000_000))
        unsupported = self.paths.audio / "ignore.txt"
        unsupported.write_text("ignore", encoding="utf-8")
        stale_file = self.paths.rss_episodes / "stale.wav"
        stale_file.write_bytes(b"stale")

        result = self.service.rebuild_feed("http://127.0.0.1:8000")

        self.assertFalse(stale_file.exists())
        self.assertEqual([path.name for path in result.staged_episode_paths], ["older.mp3", "newest.wav"])
        self.assertEqual((self.paths.rss / "podcast.xml").read_text(encoding="utf-8").count("<item>"), 2)
        feed_text = result.feed_path.read_text(encoding="utf-8")
        self.assertIn('url="http://127.0.0.1:8000/episodes/older.mp3"', feed_text)
        self.assertIn('type="audio/mpeg"', feed_text)
        self.assertIn('url="http://127.0.0.1:8000/episodes/newest.wav"', feed_text)
        self.assertIn('type="audio/wav"', feed_text)

    def test_rebuild_feed_raises_when_no_audio_exists(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.service.rebuild_feed("http://127.0.0.1:8000")

        self.assertIn("Generate audio before starting local RSS delivery", str(ctx.exception))

    def test_build_public_base_url_uses_public_host_flag(self) -> None:
        url = self.service.build_public_base_url(bind_host="0.0.0.0", port=8000, public_host="1.2.3.4")
        self.assertEqual(url, "http://1.2.3.4:8000")

    def test_build_public_base_url_uses_env_var(self) -> None:
        os.environ["PODCAST_BASE_URL"] = "http://203.0.113.5:8000"
        try:
            url = self.service.build_public_base_url(bind_host="0.0.0.0", port=9000)
        finally:
            del os.environ["PODCAST_BASE_URL"]
        self.assertEqual(url, "http://203.0.113.5:8000")

    def test_build_public_base_url_env_var_strips_trailing_slash(self) -> None:
        os.environ["PODCAST_BASE_URL"] = "http://203.0.113.5:8000/"
        try:
            url = self.service.build_public_base_url(bind_host="0.0.0.0", port=9000)
        finally:
            del os.environ["PODCAST_BASE_URL"]
        self.assertEqual(url, "http://203.0.113.5:8000")

    def test_build_public_base_url_public_host_overrides_env_var(self) -> None:
        os.environ["PODCAST_BASE_URL"] = "http://203.0.113.5:8000"
        try:
            url = self.service.build_public_base_url(bind_host="0.0.0.0", port=9000, public_host="5.6.7.8")
        finally:
            del os.environ["PODCAST_BASE_URL"]
        self.assertEqual(url, "http://5.6.7.8:9000")

    def test_build_public_base_url_falls_back_to_hostname(self) -> None:
        os.environ.pop("PODCAST_BASE_URL", None)
        url = self.service.build_public_base_url(bind_host="127.0.0.1", port=8000)
        self.assertEqual(url, "http://127.0.0.1:8000")

    def test_create_server_serves_feed_and_episode(self) -> None:
        audio_path = self.paths.audio / "episode.wav"
        audio_path.write_bytes(b"episode-bytes")
        server = self.service.create_server(host="127.0.0.1", port=0)
        port = int(server.server_address[1])
        result = self.service.rebuild_feed(f"http://127.0.0.1:{port}")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with urllib.request.urlopen(result.feed_url) as response:
                feed_body = response.read().decode("utf-8")
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/episodes/episode.wav") as response:
                episode_body = response.read()
                content_type = response.headers.get_content_type()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertIn("<rss", feed_body)
        self.assertIn("episode.wav", feed_body)
        self.assertEqual(episode_body, b"episode-bytes")
        self.assertIn(content_type, {"audio/wav", "audio/x-wav"})
