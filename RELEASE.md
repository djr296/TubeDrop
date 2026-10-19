# TubeDrop for Windows

## v1.0.3

- Added an optional **YouTube sign-in** selector for Chrome and Edge.
- Fixes YouTube's “Sign in to confirm you're not a bot” response by using the selected browser's existing local session.
- Browser cookies remain on the user's computer and are never stored or uploaded by TubeDrop.

### Previous v1.0.2 fixes

- Fixed recurring YouTube downloads failing with `HTTP Error 403: Forbidden` after YouTube's October 2026 playback changes.
- Updated the bundled yt-dlp engine to nightly version 2026.10.10.233141.
- Bundled Deno and yt-dlp's EJS challenge solver, which current YouTube playback requires.
- Enabled official EJS script refreshes from yt-dlp's GitHub project for better resilience to future script-only changes.

## Install

1. Extract the entire release ZIP to a folder.
2. Install FFmpeg once from Windows Terminal or PowerShell:

   ```powershell
   winget install --id Gyan.FFmpeg.Essentials --exact
   ```

3. Close and reopen TubeDrop after FFmpeg finishes installing.
4. Run `TubeDrop.exe`.

TubeDrop is currently unsigned, so Windows SmartScreen may display an **Unknown publisher** warning. Verify the SHA-256 checksum published beside the release before running it.

## Usage

Paste a YouTube video link, choose MP3 audio or MP4 video up to 1080p, select a destination folder, and click **Download now**. Only download media you own or have permission to save.

## Included files

- `TubeDrop.exe` — the Windows application
- `LICENSE` — TubeDrop's MIT license
- `THIRD_PARTY_NOTICES.md` — dependency, FFmpeg, and artwork notices
- `LICENSE-DENO.md` — license for the bundled Deno runtime
- `README.md` — project documentation

FFmpeg is not included in the release ZIP and remains separately installed software under its own license.
