# Third-party notices

TubeDrop depends on the following open-source projects. Their licenses remain applicable to their respective components:

| Component | Purpose | License |
| --- | --- | --- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Media extraction and download engine | The Unlicense |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Desktop interface toolkit | CC0 1.0 Universal |
| [Pillow](https://python-pillow.github.io/) | Seasonal background loading and resizing | MIT-CMU |
| [PyInstaller](https://pyinstaller.org/) | Windows executable packaging (development dependency) | GPL-2.0-or-later with a special exception for distributing bundled applications |
| [Deno](https://deno.com/) | Sandboxed JavaScript runtime for YouTube challenge solving | MIT |
| [yt-dlp-ejs](https://github.com/yt-dlp/ejs) | YouTube JavaScript challenge solver scripts | Unlicense |

The Windows release bundles Deno 2.9.7. Its license is included beside the bundled executable and remains applicable to Deno.

## FFmpeg distribution

The Windows executable produced by `build.ps1` does **not** contain FFmpeg. TubeDrop locates and invokes a separately installed `ffmpeg` executable as a subprocess. Users can install the Gyan FFmpeg Essentials package with Windows Package Manager as described in the README.

FFmpeg is separate software distributed under its own license. Gyan's current static Windows builds are GPLv3. Users and downstream distributors should consult the license that accompanies the exact FFmpeg package they install or redistribute.

- FFmpeg license and legal information: <https://ffmpeg.org/legal.html>
- FFmpeg source: <https://ffmpeg.org/download.html#get-sources>
TubeDrop invokes FFmpeg as a separate executable. No claim of ownership is made over FFmpeg or any other third-party component, and TubeDrop does not redistribute it.

## Seasonal artwork

The five images under `assets/seasons/` were generated for this project with OpenAI's image-generation tooling. They may be used, modified, and distributed with TubeDrop, subject to the OpenAI terms applicable to the account that generated them. The images contain no third-party logos or intentionally copied characters.

This notice is informational and is not legal advice.
