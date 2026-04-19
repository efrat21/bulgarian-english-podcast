# Knigovishte Podcast Builder

Local-first Python CLI for turning a public Knigovishte article into:

1. cached source HTML
2. English translation text
3. a bilingual podcast script
4. a generated local `.wav` episode

## What is implemented

- `plan` prints the artifact paths that will be used for a URL or filter-selected article.
- `fetch` downloads a Knigovishte article, parses the Bulgarian title/body, and caches the HTML.
- `translate` calls Langbly and saves ordered English sentence pairs.
- `build-script` formats the bilingual episode script.
- `generate-audio` renders the script to a local `.wav` file, using local `pyttsx3` for English and Google Cloud TTS for Bulgarian by default.
- `run` executes the full fetch → translate → script → audio pipeline.
- `web` starts a small local Flask UI for running the same pipeline in a browser.

**NEW:** All commands now support filter-based article selection via `--filter` flag, allowing automatic selection of articles by length or category. Without explicit `--url`, the latest article is selected by default.

The app is already wired end to end. It is not a scaffold-only README anymore.

## Environment requirements

- Python **3.11+**
- Windows-friendly local environment
- Internet access for `fetch`, `translate`, `build-script`, `generate-audio`, and `run`
- A valid `LANGBLY_API_KEY` for any command that translates text
- A working local speech engine supported by `pyttsx3` for English audio generation
- Google Cloud Text-to-Speech credentials for Bulgarian audio generation

Install dependencies:

```powershell
pip install -r requirements.txt
```

Install the local package plus developer tooling:

```powershell
pip install -e ".[dev]"
```

Minimal `.env` in `my-project\`:

```dotenv
LANGBLY_API_KEY=your_key_here
```

Optional translation override:

```dotenv
LANGBLY_BASE_URL=https://api.langbly.com
```

Bulgarian audio defaults to Google Cloud voice `bg-BG-Standard-B`. Configure credentials with the standard Google env var:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
```

Optional Bulgarian voice overrides:

```powershell
$env:GOOGLE_TTS_BG_VOICE_NAME="bg-BG-Standard-B"
$env:GOOGLE_TTS_BG_LANGUAGE_CODE="bg-BG"
```

## Key commands

Run from `my-project\`.

### With explicit URL

```powershell
python main.py plan --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py translate --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py build-script --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py run --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --refresh
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --en-voice "zira" --bg-voice "bg-BG-Standard-B"
python main.py web
```

### With filter-based article selection

```powershell
# Get the latest article (no filter specified)
python main.py run

# Filter by article length (sentence count)
# Edit filters.json with: {"min_length": 10, "max_length": 50}
python main.py run --filter filters.json

# Use a custom filter file
python main.py fetch --filter my-custom-filters.json
```

### Filter configuration

Create a JSON file (e.g., `filters.json`) with optional filtering criteria:

```json
{
  "min_length": 10,
  "max_length": 50,
  "category": null
}
```

Supported filters:
- `min_length`: Minimum number of sentences (null = no minimum)
- `max_length`: Maximum number of sentences (null = no maximum)
- `category`: Reserved for future category filtering (not yet implemented)

### Testing

```powershell
python -m unittest discover -s tests -v
```

Package-style entry points also work after install:

```powershell
python -m knigovishte_podcast plan --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
knigovishte-podcast run --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
knigovishte-podcast run --filter filters.json
knigovishte-podcast web --port 5000
```

## Local web UI

Run from `my-project\`:

```powershell
python main.py web
```

Then open `http://127.0.0.1:5000` in your browser.

- Paste a Knigovishte article URL, or leave the field blank to use the latest article automatically.
- Submit the form to run the existing pipeline.
- The page shows the generated artifact paths and links to the output folder/files under `data\`.

## Quality checks

Run from `my-project\`.

```powershell
ruff check main.py src tests
mypy main.py src
python -m unittest discover -s tests -v
python -m build
```

GitHub Actions now runs the same lint, type-check, test, and package-build flow on pushes and pull requests that touch the app or workflow.

## Artifact layout

- `data\articles\{slug}.html` — cached source HTML
- `data\scripts\{slug}.translation.txt` — translation artifact
- `data\scripts\{slug}.txt` — bilingual podcast script
- `data\audio\{slug}.wav` — generated audio
- `data\audio\manifest.json` — durable article-content hash registry used to skip duplicate audio generation

The CLI is local-first: cached article HTML is reused unless `--refresh` is passed. Once an article has produced audio, later `run` or `generate-audio` calls for the same article content reuse the manifest entry and skip creating a duplicate `.wav`.

## Architecture

```text
Knigovishte URL
   -> KnigovishteArticleFetcher
   -> LangblyTranslator
   -> PodcastScriptBuilder
   -> mixed local/Google TTS
   -> local artifacts in data\
```

Key code paths:

- `src\knigovishte_podcast\cli.py` — command parsing and user-facing workflow
- `src\knigovishte_podcast\pipeline.py` — end-to-end orchestration
- `src\knigovishte_podcast\services\dedup.py` — article hash manifest for durable audio deduplication
- `src\knigovishte_podcast\services\fetcher.py` — Knigovishte fetch + parse
- `src\knigovishte_podcast\services\translator.py` — Langbly API adapter
- `src\knigovishte_podcast\services\script_builder.py` — bilingual script formatter
- `src\knigovishte_podcast\services\tts.py` — mixed local/Google audio generation
- `tests\` — unittest coverage for CLI, pipeline, and service boundaries

## Current limitations

- Fetching only supports public Knigovishte article pages that still use the current `kmedia-article-title` and `kmedia-article-content` structure.
- Sentence splitting is heuristic and may mishandle Bulgarian abbreviations or unusual punctuation.
- Translation depends on Langbly availability, credentials, and response shape.
- Audio generation currently targets local `.wav` output only.
- English `pyttsx3` voice availability varies by machine and installed system voices.
- Bulgarian synthesis depends on Google Cloud credentials and network access; the default configured voice is `bg-BG-Standard-B`.
- Filter-based selection scans the Knigovishte listing page and fetches articles sequentially; performance depends on network and filter criteria.
- Category filtering is reserved for future implementation when article metadata becomes available.

## Packaging and deployment strategy

- Ship the app as a normal Python package built from `pyproject.toml`.
- The practical distribution unit today is a wheel or source archive created with `python -m build`.
- Install locally with `pip install .` or `pip install dist\knigovishte_podcast-0.1.0-py3-none-any.whl`.
- Do **not** add Docker or hosted deployment yet; this is a local CLI, not a long-running service.

## Developer notes

- Main package path: `src\knigovishte_podcast\`
- Runtime config lives in `src\knigovishte_podcast\config.py`
- `ProjectPaths.ensure()` creates the stable local artifact folders on demand
- Tests currently run with `unittest`, not `pytest`
