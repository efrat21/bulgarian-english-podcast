# Knigovishte Podcast Builder

Starter scaffold for a local-first app that will:

1. fetch a Bulgarian article from `https://www.knigovishte.bg/`
2. translate it to English
3. generate a podcast-style audio file

## Why this stack

- **Python 3.11+**
- **stdlib-first scaffold**
- **CLI-oriented structure**

This keeps the first step simple on Windows, fits scraping/translation/TTS well, and leaves cheap extension points for site parsing, translation providers, and audio generation later.

## Current shape

- `src\knigovishte_podcast\` — application package
- `src\knigovishte_podcast\services\` — pipeline boundaries
- `tests\` — unit tests for deterministic logic
- `data\articles\` — fetched source material
- `data\scripts\` — generated podcast scripts
- `data\audio\` — generated audio files

Implemented today:

- `KnigovishteArticleFetcher` downloads a public Knigovishte/Vijte article page, extracts the Bulgarian title, and splits article text into Bulgarian sentences.
- `LangblyTranslator` translates the title plus article sentences as one ordered batch.
- `PodcastScriptBuilder` formats the bilingual podcast script.
- `Pyttsx3PodcastAudioGenerator` renders the script to a local `.wav` file.
- `ArticleToPodcastPipeline` caches fetched HTML, writes the generated script, and hands the script to TTS behind one stable interface.

## Planned flow

1. `KnigovishteArticleFetcher` extracts title and Bulgarian sentences
2. `ArticleTranslator` produces English title and sentence pairs
3. `PodcastScriptBuilder` formats the bilingual script
4. `PodcastAudioGenerator` renders audio from the script

## Commands to use once Python is available

```powershell
python main.py plan --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/book/1532-kolko-tezhi-edna-leka-muha"
python main.py translate --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py build-script --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py generate-audio --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py run --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha"
python main.py fetch --url "https://www.knigovishte.bg/vijte/1532-kolko-tezhi-edna-leka-muha" --refresh
python -m unittest discover -s tests
```

All commands use local-first defaults:

- article HTML cache: `data\articles\{slug}.html`
- translation text artifact: `data\scripts\{slug}.translation.txt`
- podcast script: `data\scripts\{slug}.txt`
- audio output: `data\audio\{slug}.wav`

## Fetcher limitations in this first slice

- Supports public article pages that expose the current `kmedia-article-title` and `kmedia-article-content` HTML structure.
- Ignores quiz/comment UI and image captions; it focuses on title plus article body text.
- Sentence splitting is heuristic (`.`, `!`, `?`, `…`, and line breaks), so edge cases in Bulgarian abbreviations are not handled yet.

## Current limitation

The `translate`, `build-script`, `generate-audio`, and `run` commands depend on a valid `LANGBLY_API_KEY` in `my-project\.env` or the environment.
