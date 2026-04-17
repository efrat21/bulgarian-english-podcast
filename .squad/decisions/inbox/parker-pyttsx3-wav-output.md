# Parker Decision: pyttsx3 output is wav-first

## Context

The local TTS implementation uses `pyttsx3` and is the current audio backend for the project.

## Decision

Standardize the local audio artifact on `.wav` output for the pyttsx3-backed generator and make planning/output messaging match that actual file path.

## Why

- The implementation already generates `.wav` files reliably with pyttsx3.
- Claiming `.mp3` in planning output created a mismatch between reported and real artifacts.
- Audio generation should only report success when a fresh file exists at the expected path.

## Impact

- TTS output under `my-project\\data\\audio\\` is currently `*.wav`.
- Voice selection now fails explicitly when the requested voice is unavailable.
- Future MP3 support should be a separate enhancement with an explicit conversion step or different backend.
