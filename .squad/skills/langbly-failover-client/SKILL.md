---
name: "langbly-failover-client"
description: "Harden a Langbly translation client against regional endpoint stalls without changing the translation contract."
domain: "error-handling"
confidence: "high"
source: "earned"
tools:
  - name: "powershell"
    description: "Run targeted unittest, ruff, and mypy checks from the nested Python app."
    when: "When changing translator config or HTTP client behavior."
---

## Context
Use this when a translation workflow already depends on Langbly, but a configured regional host can hang or fail intermittently. The goal is to keep the current request/response shape and add resilience at the provider boundary rather than redesigning the pipeline.

## Patterns
- Keep the configured `LANGBLY_BASE_URL` as the first attempt, but automatically append Langbly's default API host as a failover target when a custom host is configured.
- Treat transport failures and transient HTTP responses (`408`, `429`, `5xx`) as retryable; keep validation and permanent `4xx` failures strict.
- Put timeout, retry count, retry backoff, and optional extra fallback hosts in config so the CLI, web UI, and pipeline all inherit the same behavior.
- Preserve batch alignment guarantees by validating translation counts and blank `translatedText` values after a successful response, not by weakening parsing on retries.

## Examples
- `my-project\src\knigovishte_podcast\config.py` adds `timeout_seconds`, `max_retries`, `retry_backoff_seconds`, and `fallback_base_urls` to `TranslationConfig`.
- `my-project\src\knigovishte_podcast\services\translator.py` iterates across `config.all_base_urls()` before failing a batch request.
- `my-project\tests\test_translator.py` covers timeout failover from `eu.langbly.com` to the default Langbly host.

## Anti-Patterns
- Baking a single regional endpoint into code with no escape hatch.
- Retrying malformed responses that indicate batch drift or missing translated text.
- Extending total latency by adding retries without making the behavior configurable.
