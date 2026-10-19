from pathlib import Path

import pytest

from downloader import build_options, find_ffmpeg, find_javascript_runtime, is_youtube_url


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtube.com/shorts/abc123",
    "https://m.youtube.com/live/abc123",
])
def test_accepts_video_urls(url: str) -> None:
    assert is_youtube_url(url)


@pytest.mark.parametrize("url", [
    "", "youtube.com", "https://example.com/watch?v=abc",
    "https://youtube.com/playlist?list=abc", "javascript:alert(1)",
])
def test_rejects_invalid_or_non_video_urls(url: str) -> None:
    assert not is_youtube_url(url)


def test_mp3_options_extract_audio(tmp_path: Path) -> None:
    options = build_options("mp3", tmp_path, lambda _: None, lambda _: None)
    assert options["noplaylist"] is True
    assert options["postprocessors"][0]["preferredcodec"] == "mp3"


def test_mp4_options_cap_resolution(tmp_path: Path) -> None:
    options = build_options("mp4", tmp_path, lambda _: None, lambda _: None, javascript_runtime="deno.exe")
    assert "height<=1080" in options["format"]
    assert options["merge_output_format"] == "mp4"
    assert options["js_runtimes"] == {"deno": {"path": "deno.exe"}}
    assert options["remote_components"] == {"ejs:github"}


def test_find_ffmpeg_reports_install_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("downloader.shutil.which", lambda _: None)
    with pytest.raises(RuntimeError, match="winget install"):
        find_ffmpeg()


def test_find_javascript_runtime_reports_reinstall(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("downloader.resource_path", lambda *_: Path("missing-deno.exe"))
    monkeypatch.setattr("downloader.shutil.which", lambda _: None)
    with pytest.raises(RuntimeError, match="Reinstall"):
        find_javascript_runtime()
