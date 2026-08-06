# TubeDrop

A small Windows desktop app for saving a single YouTube video as MP3 audio or an MP4 video at up to 1080p.

The rounded, resizable interface includes five selectable seasonal themes—Summer, Winter, Halloween, Fall, and Spring—each with its own illustrated background and matching color palette.

Only download videos you own or have permission to save. YouTube availability, restrictions, and terms still apply.

## Run from source

Requires Windows 10/11 and Python 3.10 or newer.

```powershell
python -m pip install -r requirements.txt
python app.py
```

The packaged FFmpeg component is located automatically; the user does not need to install FFmpeg separately.

## Build the Windows executable

```powershell
.\build.ps1
```

The standalone app is written to `dist\TubeDrop.exe`. The first build can take several minutes while dependencies are installed.

## Notes

- MP4 means the best available video no higher than 1080p, merged with the best available audio.
- MP3 uses the best available audio source and high-quality variable-bitrate conversion.
- Playlist URLs are intentionally rejected and playlist expansion is disabled.
- Some restricted, private, paid, or age-gated videos may not be downloadable without account cookies; this app does not collect browser credentials.
