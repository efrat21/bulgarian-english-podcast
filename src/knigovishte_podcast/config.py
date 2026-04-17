from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data: Path
    articles: Path
    scripts: Path
    audio: Path

    @classmethod
    def from_root(cls, root: Path | None = None) -> "ProjectPaths":
        project_root = root or Path(__file__).resolve().parents[2]
        data = project_root / "data"
        return cls(
            root=project_root,
            data=data,
            articles=data / "articles",
            scripts=data / "scripts",
            audio=data / "audio",
        )

    def ensure(self) -> None:
        for directory in (self.data, self.articles, self.scripts, self.audio):
            directory.mkdir(parents=True, exist_ok=True)


def episode_slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    raw = parsed.path.strip("/") or parsed.netloc or "episode"
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "episode"


@dataclass(frozen=True)
class TranslationConfig:
    api_key: str
    base_url: str = "https://api.langbly.com"
    source_lang: str = "bg"
    target_lang: str = "en"

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "TranslationConfig":
        """Load translation config from .env file in project root."""
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        api_key = os.getenv("LANGBLY_API_KEY")
        if not api_key:
            raise ValueError(
                "LANGBLY_API_KEY not found in .env file or environment. "
                "Create .env with LANGBLY_API_KEY=your_key"
            )
        
        base_url = os.getenv("LANGBLY_BASE_URL", "https://api.langbly.com")
        return cls(api_key=api_key, base_url=base_url)
