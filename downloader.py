from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
from typing import Callable, Literal
from urllib.parse import parse_qs, urlparse


DownloadKind = Literal["mp3", "mp4"]
CookieBrowser = Literal["chrome", "edge", "firefox"]


class DownloadCancelled(Exception):
    pass


@dataclass(frozen=True)
class Progress:
    percent: float | None
    status: str
    detail: str = ""


def resource_path(*parts: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return root.joinpath(*parts)


def find_javascript_runtime() -> str:
    bundled = resource_path("tools", "deno", "deno.exe")
    if bundled.is_file():
        return str(bundled)
    deno = shutil.which("deno")
    if deno:
        return deno
    raise RuntimeError(
        "TubeDrop's JavaScript runtime is missing. Reinstall the latest TubeDrop release."
    )


def find_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise RuntimeError(
        "FFmpeg is required for MP3 conversion and 1080p video merging. "
        "Install it from Windows Terminal with:\n\n"
        "winget install --id Gyan.FFmpeg.Essentials --exact"
    )


def is_youtube_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if parsed.scheme not in {"http", "https"}:
        return False
    if host == "youtu.be":
        return bool(parsed.path.strip("/"))
    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            return bool(parse_qs(parsed.query).get("v"))
        parts = parsed.path.strip("/").split("/")
        return len(parts) == 2 and parts[0] in {"shorts", "live"} and bool(parts[1])
    return False


def build_options(
    kind: DownloadKind,
    output_dir: Path,
    progress_hook: Callable[[dict], None],
    postprocessor_hook: Callable[[dict], None],
    ffmpeg_location: str | None = None,
    javascript_runtime: str | None = None,
    cookie_browser: CookieBrowser | None = None,
) -> dict:
    options: dict = {
        "outtmpl": str(output_dir / "%(title).180B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "windowsfilenames": True,
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "quiet": True,
        "no_warnings": True,
        "overwrites": False,
        # Permit yt-dlp to refresh its signed EJS challenge scripts when YouTube
        # changes them, avoiding a full TubeDrop rebuild for script-only updates.
        "remote_components": {"ejs:github"},
    }
    if ffmpeg_location:
        options["ffmpeg_location"] = ffmpeg_location
    if javascript_runtime:
        options["js_runtimes"] = {"deno": {"path": javascript_runtime}}
    if cookie_browser:
        # yt-dlp reads the selected browser's local cookie database directly.
        # TubeDrop never copies, uploads, or stores the cookies itself.
        options["cookiesfrombrowser"] = (cookie_browser,)

    if kind == "mp3":
        options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                    },
                    {"key": "FFmpegMetadata", "add_metadata": True},
                ],
            }
        )
    else:
        options.update(
            {
                "format": (
                    "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo[height<=1080]+bestaudio/"
                    "best[height<=1080][ext=mp4]/best[height<=1080]"
                ),
                "merge_output_format": "mp4",
                "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
            }
        )
    return options


def download(
    url: str,
    kind: DownloadKind,
    output_dir: Path,
    on_progress: Callable[[Progress], None],
    should_cancel: Callable[[], bool],
    cookie_browser: CookieBrowser | None = None,
) -> None:
    if not is_youtube_url(url):
        raise ValueError("Enter a valid YouTube video, Short, or live-video URL.")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("Required download components are not installed.") from exc

    ffmpeg_path = find_ffmpeg()
    javascript_runtime = find_javascript_runtime()

    def check_cancel() -> None:
        if should_cancel():
            raise DownloadCancelled("Download cancelled.")

    def progress_hook(data: dict) -> None:
        check_cancel()
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else None
            speed = data.get("_speed_str", "").strip()
            eta = data.get("_eta_str", "").strip()
            detail = "  •  ".join(part for part in (speed, f"ETA {eta}" if eta else "") if part)
            on_progress(Progress(percent, "Downloading…", detail))
        elif status == "finished":
            on_progress(Progress(100, "Download complete. Processing…"))

    def postprocessor_hook(data: dict) -> None:
        check_cancel()
        if data.get("status") == "started":
            on_progress(Progress(None, "Converting audio…" if kind == "mp3" else "Merging video…"))

    options = build_options(
        kind,
        output_dir,
        progress_hook,
        postprocessor_hook,
        ffmpeg_path,
        javascript_runtime,
        cookie_browser,
    )
    on_progress(Progress(0, "Reading video information…"))
    with YoutubeDL(options) as ydl:
        result = ydl.download([url.strip()])
    if result != 0:
        raise RuntimeError("The download did not complete successfully.")
    check_cancel()
    on_progress(Progress(100, "Done!"))
