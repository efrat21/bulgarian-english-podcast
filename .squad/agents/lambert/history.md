# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Testing will need to cover the full fetch → translate → audio pipeline, not just individual functions.
- The coverage gap was mostly execution-path, not missing files: translator tests existed but were not discoverable by unittest, so confidence improved by converting them into runnable suite coverage and adding failure-path checks for CLI and pipeline fallbacks.
