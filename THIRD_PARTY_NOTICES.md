# Third-party notices

TubeDrop depends on the following open-source projects. Their licenses remain applicable to their respective components:

| Component | Purpose | License |
| --- | --- | --- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Media extraction and download engine | The Unlicense |
| [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | FFmpeg binary discovery and packaging | BSD 2-Clause |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Desktop interface toolkit | CC0 1.0 Universal |
| [Pillow](https://python-pillow.github.io/) | Seasonal background loading and resizing | MIT-CMU |
| [PyInstaller](https://pyinstaller.org/) | Windows executable packaging (development dependency) | GPL-2.0-or-later with a special exception for distributing bundled applications |

## FFmpeg distribution

The Windows executable produced by `build.ps1` includes the FFmpeg executable supplied by `imageio-ffmpeg`. The currently resolved Windows binary reports that it was built with `--enable-gpl --enable-version3`, so that FFmpeg binary is covered by the GNU General Public License version 3 or later.

Anyone distributing a built `TubeDrop.exe` must satisfy the corresponding FFmpeg license obligations, including providing the applicable license text and complete corresponding source (or another method permitted by that license). Consult the exact FFmpeg binary's `-version` output and distribution source when preparing a release because the resolved binary may change between dependency versions.

- FFmpeg license and legal information: <https://ffmpeg.org/legal.html>
- FFmpeg source: <https://ffmpeg.org/download.html#get-sources>
- ImageIO-FFmpeg licensing notes: <https://github.com/imageio/imageio-ffmpeg#license>

TubeDrop invokes FFmpeg as a separate executable. No claim of ownership is made over FFmpeg or any other third-party component.

## Seasonal artwork

The five images under `assets/seasons/` were generated for this project with OpenAI's image-generation tooling. They may be used, modified, and distributed with TubeDrop, subject to the OpenAI terms applicable to the account that generated them. The images contain no third-party logos or intentionally copied characters.

This notice is informational and is not legal advice.
