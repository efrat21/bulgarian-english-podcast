# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Testing will need to cover the full fetch → translate → audio pipeline, not just individual functions.
- The coverage gap was mostly execution-path, not missing files: translator tests existed but were not discoverable by unittest, so confidence improved by converting them into runnable suite coverage and adding failure-path checks for CLI and pipeline fallbacks.
- Environment validation: Bulgarian TTS voice generation is not supported on this machine; SAPI backend exposes English voices only; voice-not-available error correctly raised on explicit Bulgarian requests.

## Recent Session (20260417T183932Z)

📌 **Bulgarian Voice Validation Complete**
- Independent verification that environment cannot synthesize Bulgarian speech
- Confirmed SAPI voice enumeration: English-only voices available
- Explicit Bulgarian voice request fails as expected with voice-not-available error
- Edge case validated: error is raised, not silently falling back to wrong language

## Team Updates

📌 Team update (2026-04-17T18:39:32Z): Bulgarian voice validation confirmed — environment (pyttsx3/SAPI) exposes only English voices; no Bulgarian voice available on local machine; explicit voice-not-available errors working as designed. Verified by Parker & Lambert
