# Knigovishte Podcast Builder

Local-first Python CLI for turning a public Knigovishte article into:

1. cached source HTML
2. English translation text
3. a bilingual podcast script
4. a generated local `.wav` episode

## What is implemented

- `plan` prints the artifact paths that will be used for a URL.
- `fetch` downloads a Knigovishte article, parses the Bulgarian title/body, and caches the HTML.
- `translate` calls Langbly and saves ordered English sentence pairs.
- `build-script` formats the bilingual episode script.
- `generate-audio` renders the script to a local `.wav` file with `pyttsx3`.
- `run` executes the full fetch → translate → script → audio pipeline.

The app is wired end to end and is not a scaffold-only README.

## Environment requirements

- Python **3.11+**
- Internet access for `fetch`, `translate`, `build-script`, `generate-audio`, and `run`
- A valid `LANGBLY_API_KEY` for any command that translates text
- A working local speech engine supported by `pyttsx3` for audio generation

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the local package plus developer tooling:

```bash
pip install -e ".[dev]"
```

Minimal `.env` in the repository root:

```dotenv
LANGBLY_API_KEY=your_key_here
```

Optional override:

```dotenv
LANGBLY_BASE_URL=https://api.langbly.com
```

## Key commands

Run from the repository root.

```bash
python main.py plan --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py translate --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py build-script --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py run --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --refresh
python -m unittest discover -s tests -v
```

Package-style entry points also work after install:

```bash
python -m knigovishte_podcast plan --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
knigovishte-podcast run --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
```

## Quality checks

Run from the repository root.

```bash
ruff check main.py src tests
mypy main.py src
python -m unittest discover -s tests -v
python -m build
```

GitHub Actions runs the same lint, type-check, test, and package-build flow on pushes and pull requests.

## Artifact layout

- `data/articles/{slug}.html` — cached source HTML
- `data/scripts/{slug}.translation.txt` — translation artifact
- `data/scripts/{slug}.txt` — bilingual podcast script
- `data/audio/{slug}.wav` — generated audio

The CLI is local-first: cached article HTML is reused unless `--refresh` is passed.

## Architecture

```text
Knigovishte URL
   -> KnigovishteArticleFetcher
   -> LangblyTranslator
   -> PodcastScriptBuilder
   -> Pyttsx3PodcastAudioGenerator
   -> local artifacts in data/
```

Key code paths:

- `src/knigovishte_podcast/cli.py` — command parsing and user-facing workflow
- `src/knigovishte_podcast/pipeline.py` — end-to-end orchestration
- `src/knigovishte_podcast/services/fetcher.py` — Knigovishte fetch + parse
- `src/knigovishte_podcast/services/translator.py` — Langbly API adapter
- `src/knigovishte_podcast/services/script_builder.py` — bilingual script formatter
- `src/knigovishte_podcast/services/tts.py` — local audio generation
- `tests/` — unittest coverage for CLI, pipeline, and service boundaries

## Current limitations

- Fetching only supports public Knigovishte article pages that still use the current `kmedia-article-title` and `kmedia-article-content` structure.
- Sentence splitting is heuristic and may mishandle Bulgarian abbreviations or unusual punctuation.
- Translation depends on Langbly availability, credentials, and response shape.
- Audio generation currently targets local `.wav` output only.
- `pyttsx3` voice availability varies by machine and installed system voices.

## Packaging and deployment strategy

- Ship the app as a normal Python package built from `pyproject.toml`.
- The practical distribution unit today is a wheel or source archive created with `python -m build`.
- Install locally with `pip install .` or `pip install dist/knigovishte_podcast-0.1.0-py3-none-any.whl`.
- Do **not** add Docker or hosted deployment yet; this is a local CLI, not a long-running service.

## Developer notes

- Main package path: `src/knigovishte_podcast/`
- Runtime config lives in `src/knigovishte_podcast/config.py`
- `ProjectPaths.ensure()` creates the stable local artifact folders on demand
- Tests run with `unittest`, not `pytest`
