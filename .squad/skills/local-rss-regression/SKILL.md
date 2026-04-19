# Local RSS Regression

Use this pattern when a feature writes local delivery artifacts and also serves them over HTTP.

## Pattern

1. Create filesystem fixtures in the real project path layout (`data\audio`, `data\scripts`, `data\rss`).
2. Assert feed generation first: copied enclosure files, `podcast.xml` contents, item ordering, content types, and stale-file cleanup.
3. Add CLI tests for both `--no-serve` and serving mode so feed creation and server startup/shutdown stay covered separately.
4. Finish with one live local server smoke test (`ThreadingHTTPServer` on port `0`) that fetches both the feed and an episode file.

## Why

This catches the handoff seams that unit-only tests miss: filesystem preparation, XML publishing, LAN-serving entrypoints, and subscriber-facing enclosure URLs.
