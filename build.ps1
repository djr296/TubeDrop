$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install --upgrade -r requirements-dev.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name TubeDrop `
    --add-data "assets;assets" `
    --collect-all customtkinter `
    --collect-all yt_dlp `
    --collect-all imageio_ffmpeg `
    app.py

Write-Host "Built: $ProjectRoot\dist\TubeDrop.exe"
