# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Language work will likely include translation quality, normalization, and preparation for TTS.
- Langbly translation now lives in `my-project\src\knigovishte_podcast\services\translator.py` and keeps the batch boundary explicit by sending title + sentence list in source order.
- Translator validation is part of the provider wrapper: reject partial/malformed Langbly batch responses before they can drift sentence alignment.
- Current dependency audit is reflected in `my-project\requirements.txt`; active non-stdlib imports remain `requests`, `python-dotenv`, and `pyttsx3`.

## Team Updates

📌 Langbly translator decision (2026-04-17): Use Langbly API as the backend provider for ArticleTranslator interface. User preference for translation implementation. — decided by User
