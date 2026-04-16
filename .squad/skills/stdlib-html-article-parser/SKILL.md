---
name: "stdlib-html-article-parser"
description: "How to add a first-slice web article fetcher without committing to third-party parsing libraries too early."
domain: "parsing"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Add a focused fetcher, tests, and docs in one surgical change."
    when: "A stdlib-first project needs to prove one source site's HTML shape before upgrading tooling."
---

## Context

Use this when a pipeline needs a real fetcher now, but the source site's structure is only partially known and the team wants to keep setup friction low.

## Patterns

- Keep the public boundary small: `fetch(url)` for normal use, with `fetch_html(url)` and `parse_html(url, html)` underneath for caching and tests.
- Use `urllib.request` with a user agent and language headers for simple public-page retrieval.
- Use `HTMLParser` to target stable containers such as a page title element and a main article-content element.
- Drop obvious non-article chrome early (comments, quiz UI, captions, scripts, styles) before sentence splitting.
- Make sentence splitting explicitly heuristic in the first slice and document that limitation.

## Examples

- `my-project\src\knigovishte_podcast\services\fetcher.py` implements a Knigovishte parser around `kmedia-article-title` and `kmedia-article-content`.
- `my-project\tests\test_fetcher.py` verifies parsing with inline HTML fixtures and no network dependency.
- `my-project\src\knigovishte_podcast\cli.py` uses the split boundary to cache fetched HTML after parsing succeeds.

## Anti-Patterns

- Pulling in BeautifulSoup or browser automation before the basic article shape is proven.
- Hiding parsing behind a single network-only method that cannot be tested with fixtures.
- Silently scraping unrelated page chrome instead of failing fast when the expected article container is missing.
