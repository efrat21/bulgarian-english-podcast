from __future__ import annotations

import shutil
import socket
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from ..config import ProjectPaths

SUPPORTED_AUDIO_EXTENSIONS = (".mp3", ".m4a", ".aac", ".wav")
CONTENT_TYPES = {
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".wav": "audio/wav",
}


@dataclass(frozen=True)
class FeedBuildResult:
    feed_path: Path
    feed_url: str
    staged_episode_paths: tuple[Path, ...]


class LocalRSSService:
    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def build_public_base_url(
        self,
        *,
        bind_host: str,
        port: int,
        public_host: str | None = None,
    ) -> str:
        host = public_host or self._default_public_host(bind_host)
        return f"http://{host}:{port}"

    def rebuild_feed(self, public_base_url: str) -> FeedBuildResult:
        self.paths.ensure()
        audio_files = self._discover_audio_files()
        if not audio_files:
            raise ValueError(
                f"No supported audio files found in {self.paths.audio}. "
                "Generate audio before starting local RSS delivery."
            )

        self._clean_directory(self.paths.rss_episodes)
        staged_episode_paths = []
        for audio_path in audio_files:
            staged_path = self.paths.rss_episodes / audio_path.name
            shutil.copy2(audio_path, staged_path)
            staged_episode_paths.append(staged_path)

        feed_path = self.paths.rss / "podcast.xml"
        feed_url = f"{public_base_url.rstrip('/')}/podcast.xml"
        feed_path.write_bytes(
            self._render_feed_xml(
                public_base_url=public_base_url.rstrip("/"),
                staged_episode_paths=tuple(staged_episode_paths),
            )
        )
        return FeedBuildResult(
            feed_path=feed_path,
            feed_url=feed_url,
            staged_episode_paths=tuple(staged_episode_paths),
        )

    def create_server(self, *, host: str, port: int) -> ThreadingHTTPServer:
        handler = partial(SimpleHTTPRequestHandler, directory=str(self.paths.rss))
        return ThreadingHTTPServer((host, port), handler)

    def _default_public_host(self, bind_host: str) -> str:
        if bind_host in {"0.0.0.0", "::", ""}:
            return socket.gethostname()
        return bind_host

    def _discover_audio_files(self) -> list[Path]:
        files = [
            path
            for path in self.paths.audio.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
        ]
        return sorted(files, key=lambda path: (-path.stat().st_mtime, path.name.lower()))

    def _clean_directory(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        for child in directory.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    def _render_feed_xml(
        self,
        *,
        public_base_url: str,
        staged_episode_paths: tuple[Path, ...],
    ) -> bytes:
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Knigovishte Podcast Builder"
        ET.SubElement(channel, "link").text = f"{public_base_url}/podcast.xml"
        ET.SubElement(
            channel,
            "description",
        ).text = "Local LAN RSS feed generated from existing podcast audio artifacts."
        ET.SubElement(channel, "language").text = "en"

        for staged_path in staged_episode_paths:
            item = ET.SubElement(channel, "item")
            title = staged_path.stem.replace("-", " ").strip() or staged_path.stem
            enclosure_url = f"{public_base_url}/episodes/{quote(staged_path.name)}"
            stat = staged_path.stat()
            published_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "guid").text = enclosure_url
            ET.SubElement(item, "pubDate").text = format_datetime(published_at)
            ET.SubElement(
                item,
                "enclosure",
                url=enclosure_url,
                length=str(stat.st_size),
                type=CONTENT_TYPES[staged_path.suffix.lower()],
            )

        return ET.tostring(rss, encoding="utf-8", xml_declaration=True)
