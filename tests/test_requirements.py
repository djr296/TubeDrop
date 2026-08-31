from pathlib import Path


def test_yt_dlp_minimum_includes_august_403_fix() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "yt-dlp>=2026.8.19" in requirements
