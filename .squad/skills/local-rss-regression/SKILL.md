# Local RSS Regression

Use this pattern when a feature writes local delivery artifacts and also serves them over HTTP.

## Pattern

1. Create filesystem fixtures in the real project path layout (`data\audio`, `data\scripts`, `data\rss`).
2. Assert feed generation first: copied enclosure files, `podcast.xml` contents, item ordering, content types, stale-file cleanup, and subscriber-facing `<item><title>` values.
3. When episode titles come from persisted artifacts, add one regression where `scripts\<slug>.translation.txt` or `<slug>.txt` supplies `English title: ...`, and another where filename cleanup removes the `vijte-####` prefix if metadata is missing.
4. Add CLI tests for both `--no-serve` and serving mode so feed creation and server startup/shutdown stay covered separately.
5. Finish with one live local server smoke test (`ThreadingHTTPServer` on port `0`) that fetches both the feed and an episode file.

## Why

This catches the handoff seams that unit-only tests miss: filesystem preparation, XML publishing, LAN-serving entrypoints, and subscriber-facing metadata such as enclosure URLs and episode titles. Metadata-first title assertions are especially important for RSS because subscriber apps expose those strings directly, and filename-only checks can miss regressions around persisted translation/script artifacts.
