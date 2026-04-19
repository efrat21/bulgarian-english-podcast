from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template_string, request

from .config import ProjectPaths
from .models import PodcastPlan
from .pipeline import pipeline
from .services.article_selector import ArticleFilter, ArticleSelector
from .services.dedup import DuplicateArticleError

WEB_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("obshtestvo", "Society"),
    ("sviat", "World"),
    ("nauka", "Science"),
    ("kultura", "Culture"),
    ("sport-i-zdrave", "Sports and Health"),
    ("pishat-ni", "Letters"),
)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Knigovishte Podcast Builder</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem auto; max-width: 52rem; line-height: 1.5; }
      form { display: grid; gap: 0.75rem; padding: 1rem; border: 1px solid #d0d7de; border-radius: 0.5rem; background: #f6f8fa; }
      label { font-weight: 600; }
      input[type="text"], input[type="number"], select { width: 100%; padding: 0.6rem; }
      button { width: fit-content; padding: 0.65rem 1rem; }
      .panel { margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; }
      .success { background: #e6ffed; border: 1px solid #b7ebc6; }
      .error { background: #ffebe9; border: 1px solid #ffb3ad; }
      code { word-break: break-all; }
      ul { padding-left: 1.25rem; }
      .filters { display: grid; gap: 0.75rem; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); }
      .status { margin-top: 1rem; font-weight: 600; }
      .status[hidden] { display: none; }
    </style>
  </head>
  <body>
    <h1>Knigovishte Podcast Builder</h1>
    <p>Run the existing article → translation → script → audio pipeline locally from your browser.</p>
    <form id="podcast-form" method="post">
      <div>
        <label for="url">Article URL (optional)</label>
        <input id="url" name="url" type="text" value="{{ form.url }}" placeholder="Leave blank to use the latest Knigovishte article">
      </div>
      <div class="filters">
        <div>
          <label for="min_length">Minimum length (sentences)</label>
          <input id="min_length" name="min_length" type="number" min="1" value="{{ form.min_length }}" placeholder="Any length">
        </div>
        <div>
          <label for="max_length">Maximum length (sentences)</label>
          <input id="max_length" name="max_length" type="number" min="1" value="{{ form.max_length }}" placeholder="Any length">
        </div>
      </div>
      <div>
        <label for="category">Category</label>
        <select id="category" name="category">
          <option value="">Any category</option>
          {% for slug, label in categories %}
            <option value="{{ slug }}" {% if form.category == slug %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </div>
      <label>
        <input name="refresh" type="checkbox" {% if form.refresh %}checked{% endif %}>
        Ignore cached HTML and fetch the article again
      </label>
      <button id="submit-button" type="submit">Generate podcast artifacts</button>
    </form>
    <p id="working-message" class="status" hidden>Working...</p>

    <p><strong>Output folder:</strong> <code>{{ output_folder }}</code></p>
    <p><a href="{{ output_folder_uri }}">Output folder</a></p>

    {% if result %}
      <section class="panel success">
        <h2>{{ result.heading }}</h2>
        <p><strong>Your episode is ready.</strong></p>
        <p>{{ result.message }}</p>
        <ul>
          <li><strong>Article URL:</strong> <a href="{{ result.article_url }}">{{ result.article_url }}</a></li>
          {% if result.fetched_title %}<li><strong>Bulgarian title:</strong> {{ result.fetched_title }}</li>{% endif %}
          {% if result.translated_title %}<li><strong>English title:</strong> {{ result.translated_title }}</li>{% endif %}
          {% for artifact in result.artifacts %}
            <li><strong>{{ artifact.label }}:</strong> <code>{{ artifact.path }}</code></li>
          {% endfor %}
        </ul>
      </section>
    {% endif %}

    {% if error %}
      <section class="panel error">
        <h2>Pipeline failed</h2>
        <p>{{ error }}</p>
      </section>
    {% endif %}
    <script>
      const form = document.getElementById("podcast-form");
      const workingMessage = document.getElementById("working-message");
      const submitButton = document.getElementById("submit-button");

      if (form && workingMessage && submitButton) {
        form.addEventListener("submit", () => {
          workingMessage.hidden = false;
          submitButton.disabled = true;
          submitButton.textContent = "Working...";
        });
      }
    </script>
  </body>
</html>
""".strip()


def create_app(paths: ProjectPaths | None = None) -> Flask:
    app = Flask(__name__)
    project_paths = paths or ProjectPaths.from_root()
    project_paths.ensure()
    app.config["PROJECT_PATHS"] = project_paths

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        url_value = request.form.get("url", "").strip()
        min_length_value = request.form.get("min_length", "").strip()
        max_length_value = request.form.get("max_length", "").strip()
        category_value = request.form.get("category", "").strip()
        refresh_requested = request.form.get("refresh") == "on"
        result: dict[str, object] | None = None
        error: str | None = None

        if request.method == "POST":
            try:
                article_url, selection_message = _resolve_article_url(
                    url_value,
                    min_length=min_length_value,
                    max_length=max_length_value,
                    category=category_value,
                )
                plan = pipeline(
                    paths=project_paths,
                    use_cached_html=not refresh_requested,
                ).run(article_url)
                result = _build_success_result(plan, selection_message)
            except DuplicateArticleError as exc:
                result = {
                    "heading": "Existing audio reused",
                    "message": "This article already has generated audio, so the pipeline skipped a duplicate run.",
                    "article_url": exc.article.source_url,
                    "fetched_title": exc.article.title_bg,
                    "translated_title": None,
                    "artifacts": [_artifact("Audio output", exc.audio_path)],
                }
            except Exception as exc:
                error = str(exc)

        return render_template_string(
            PAGE_TEMPLATE,
            form={
                "url": url_value,
                "min_length": min_length_value,
                "max_length": max_length_value,
                "category": category_value,
                "refresh": refresh_requested,
            },
            result=result,
            error=error,
            categories=WEB_CATEGORIES,
            output_folder=str(project_paths.data),
            output_folder_uri=_path_uri(project_paths.data),
        )

    return app


def _resolve_article_url(
    raw_url: str,
    *,
    min_length: str = "",
    max_length: str = "",
    category: str = "",
) -> tuple[str, str]:
    if raw_url:
        return raw_url, "Used the URL you entered."

    article_filter = _build_article_filter(
        min_length=min_length,
        max_length=max_length,
        category=category,
    )
    selector = ArticleSelector()
    if article_filter is None:
        article = selector.select_article()
    else:
        article = selector.select_article(article_filter=article_filter)
    if article_filter is None:
        return (
            article.source_url,
            "No URL was provided, so the latest article was selected automatically.",
        )
    return (
        article.source_url,
        "No URL was provided, so a matching article was selected from the requested filters.",
    )


def _build_article_filter(
    *,
    min_length: str,
    max_length: str,
    category: str,
) -> ArticleFilter | None:
    normalized_category = category.strip() or None
    normalized_min = _parse_length("Minimum length", min_length)
    normalized_max = _parse_length("Maximum length", max_length)

    if (
        normalized_min is not None
        and normalized_max is not None
        and normalized_min > normalized_max
    ):
        raise ValueError("Minimum length cannot be greater than maximum length.")

    if normalized_min is None and normalized_max is None and normalized_category is None:
        return None

    return ArticleFilter(
        min_length=normalized_min,
        max_length=normalized_max,
        category=normalized_category,
    )


def _parse_length(label: str, raw_value: str) -> int | None:
    if not raw_value:
        return None

    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a whole number.") from exc

    if parsed < 1:
        raise ValueError(f"{label} must be at least 1.")

    return parsed


def _build_success_result(plan: PodcastPlan, selection_message: str) -> dict[str, object]:
    artifacts = []
    if plan.article_html_path is not None:
        artifacts.append(_artifact("Cached HTML", plan.article_html_path))
    artifacts.append(_artifact("Script output", plan.script_path))
    artifacts.append(_artifact("Audio output", plan.audio_path))
    return {
        "heading": "Podcast artifacts generated",
        "message": selection_message,
        "article_url": plan.article.source_url,
        "fetched_title": plan.article.title_bg,
        "translated_title": plan.translation.title_en,
        "artifacts": artifacts,
    }


def _artifact(label: str, path: Path) -> dict[str, str]:
    resolved_path = path.resolve()
    return {
        "label": label,
        "path": str(resolved_path),
    }


def _path_uri(path: Path) -> str:
    return path.resolve().as_uri()
