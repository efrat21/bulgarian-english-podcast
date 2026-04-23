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
- `generate-audio` renders the script to a local `.wav` file, using Google Cloud TTS standard voices for English and Bulgarian by default.
- `run` executes the full fetch → translate → script → audio pipeline.
- `web` starts a small local Flask UI for running the same pipeline in a browser.

**NEW:** All commands now support filter-based article selection via `--filter` flag, allowing automatic selection of articles by length or category. Without explicit `--url`, the latest article is selected by default.

The app is already wired end to end. It is not a scaffold-only README anymore.

## Environment requirements

- Python **3.11+**
- Windows-friendly local environment
- Internet access for `fetch`, `translate`, `build-script`, `generate-audio`, and `run`
- A valid `LANGBLY_API_KEY` for any command that translates text
- Google Cloud Text-to-Speech credentials for English and Bulgarian audio generation
- A working local speech engine supported by `pyttsx3` if you want to override either language with a local voice

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

Google audio defaults to English voice `en-US-Standard-F` and Bulgarian voice `bg-BG-Standard-B`. Configure credentials with the standard Google env var:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
```

Google Cloud English-US Standard voices currently available in the standard tier are `en-US-Standard-A` through `en-US-Standard-J`. This project defaults to `en-US-Standard-F` because it stays in the standard-price tier and gives a clear neutral female read that fits the podcast format well. If you override the English Google voice with another valid English Google voice name such as `en-GB-Standard-A`, the app keeps that segment on the Google TTS path and infers the matching language code from the voice name unless you explicitly override it.

Optional Google voice overrides:

```powershell
$env:GOOGLE_TTS_EN_VOICE_NAME="en-US-Standard-F"
$env:GOOGLE_TTS_EN_LANGUAGE_CODE="en-US"
$env:GOOGLE_TTS_BG_VOICE_NAME="bg-BG-Standard-B"
$env:GOOGLE_TTS_BG_LANGUAGE_CODE="bg-BG"
```

You can still force a local `pyttsx3` voice by passing a local voice substring on the CLI, for example:

```powershell
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --en-voice "zira"
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
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --en-voice "en-US-Standard-C" --bg-voice "bg-BG-Standard-B"
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --en-voice "zira" --bg-voice "bg-BG-Standard-B"
python main.py web
```

### Daily episode automation

Generate a new episode automatically when a new article is published:

```powershell
# Run once to check for today's article (idempotent, safe to run multiple times)
python main.py daily-check

# Run as a background daemon that checks once per day
python main.py daily-daemon

# Stop the daemon with Ctrl+C
```

The `daily-check` command:
- Fetches the latest article from Knigovishte
- Skips generation if the article URL matches the last processed article
- Skips generation if the article content matches an already-generated episode (uses existing dedup)
- Generates a new episode only when new content is found
- Saves state in `data\scheduler_state.json` so it's safe to run multiple times per day
- Handles transient errors gracefully: network failures or pipeline errors are logged but count as today's check to avoid retry spam

The `daily-daemon` command:
- Runs continuously, checking once per day for new articles
- Wakes up every hour by default to check if it's time for a daily check (configurable with `--interval`)
- Uses the same idempotent logic as `daily-check`
- Survives recoverable errors (network issues, translation failures, etc.) and continues checking future days
- Stop with Ctrl+C when you want to disable daily updates

**Scheduling with Windows Task Scheduler:**

For daily automation without a long-running daemon, schedule `daily-check` with Task Scheduler:

1. Open Task Scheduler
2. Create a new task that runs daily at your preferred time
3. Action: Start a program
   - Program: `python`
   - Arguments: `main.py daily-check`
   - Start in: `D:\first_squad_project\my-project` (or your project path)

This approach is more reliable for local machines that may sleep or restart.

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
- `category`: Category slug such as `obshtestvo`, `sviat`, `nauka`, `kultura`, `sport-i-zdrave`, or `pishat-ni`

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

## Getting the local RSS feed into Podcast Addict (Android)

Run from `my-project\` after you already have at least one generated audio file in `data\audio\`:

```powershell
python main.py local-rss-delivery
```

- The command rebuilds `data\rss\podcast.xml`, stages episode files under `data\rss\episodes\`, starts the local feed server, and prints the feed URL to use on your phone.
- If the printed host name is not reachable from Android, set the `PODCAST_BASE_URL` environment variable to your computer's Wi-Fi IPv4 address (e.g. `PODCAST_BASE_URL=http://192.168.1.10:8000` in `.env`) before running the command, or pass `--public-host <LAN-IP>` on the CLI. Use the Wi-Fi adapter address, not `127.0.0.1`.
- Keep the command running while Podcast Addict connects.

In Podcast Addict on Android:

1. Make sure the phone and computer are on the same trusted Wi-Fi network.
2. Open **Podcast Addict** → **+** → **RSS feed**.
3. Paste the printed feed URL, usually `http://<LAN-IP>:<current-port>/podcast.xml`.
4. Subscribe and refresh.

Important local-network limits:

- This feed is for a trusted LAN only. It is not a hosted or public internet feed.
- If the computer sleeps, changes networks, or you stop the local RSS command, Podcast Addict will no longer be able to refresh or download episodes.
- The current delivery path reuses local staged audio files directly; the first supported enclosure path serves the generated `.wav` output.

## Local web UI

Run from `my-project\`:

```powershell
python main.py web
```

Then open `http://127.0.0.1:5000` in your browser.

- Paste a Knigovishte article URL, or leave the field blank to use the latest article automatically.
- When the URL is blank, you can optionally narrow selection with minimum/maximum sentence length and category.
- Submit the form to run the existing pipeline; the page shows a working message while generation is in progress.
- When the run finishes, the page only shows `Your episode is ready.` and keeps a single link to the local output folder under `data\`.

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
- `data\rss\podcast.xml` — generated local RSS feed for podcast clients
- `data\rss\episodes\{filename}` — staged audio files served by the local RSS command (`.wav` today; podcast-friendly formats such as `.mp3`, `.m4a`, and `.aac` are also supported when present)

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
- `src\knigovishte_podcast\services\rss.py` — local RSS feed generation plus stdlib HTTP serving for LAN delivery
- `tests\` — unittest coverage for CLI, pipeline, and service boundaries

## Current limitations

- Fetching only supports public Knigovishte article pages that still use the current `kmedia-article-title` and `kmedia-article-content` structure.
- Sentence splitting is heuristic and may mishandle Bulgarian abbreviations or unusual punctuation.
- Translation depends on Langbly availability, credentials, and response shape.
- Audio generation currently targets local `.wav` output only, and the first local RSS delivery slice serves those staged `.wav` files directly over the LAN.
- English Google synthesis depends on Google Cloud credentials and network access; the default configured voice is `en-US-Standard-F`.
- Local `pyttsx3` fallback voice availability still varies by machine and installed system voices.
- Bulgarian synthesis depends on Google Cloud credentials and network access; the default configured voice is `bg-BG-Standard-B`.
- Filter-based selection scans the Knigovishte listing page and fetches articles sequentially; performance depends on network and filter criteria.
- Category filtering uses the matching Knigovishte category listing page before any length-based scan.

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
