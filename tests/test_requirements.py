from pathlib import Path


def test_yt_dlp_uses_current_nightly_with_ejs() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "yt-dlp[default]==2026.10.10.233141.dev0" in requirements
