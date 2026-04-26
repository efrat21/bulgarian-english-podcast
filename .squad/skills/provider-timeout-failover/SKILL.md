# Provider Timeout Failover

## When to use

Use this pattern when an external provider can be configured to hit alternate hosts or regions, and the user-facing workflow should survive one endpoint timing out.

## Pattern

1. Reproduce the exact failure host from the bug report or environment override, not just a generic network error.
2. Add a regression where the primary provider endpoint times out on the first call and a known-good fallback endpoint succeeds on the retry.
3. Assert that the retry preserves the same payload, auth headers, timeout budget, and response ordering as the original request.
4. Add one failure-path assertion for the all-endpoints-down case so the final message is intentional and timeout-specific.
5. If the provider is triggered from a user workflow such as a web form or CLI command, verify the visible outcome at that layer when behavior changes.

## First use here

- `my-project\src\knigovishte_podcast\services\translator.py`
- `my-project\tests\test_translator.py`
- `my-project\src\knigovishte_podcast\web.py`
- `my-project\tests\test_web.py`
- Drafted by Lambert while defining the approval gate for issue #24 (Langbly regional timeout during web episode generation)

## Extension

- Prefer a dedicated timeout exception from the provider seam (for example `LangblyTimeoutError`) so the user-facing layer can add explicit "no episode was generated" copy without parsing raw request text.
