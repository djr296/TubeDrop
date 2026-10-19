$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$DenoVersion = "2.9.7"
$DenoDirectory = Join-Path $ProjectRoot "tools\deno"
$DenoExecutable = Join-Path $DenoDirectory "deno.exe"
if (-not (Test-Path -LiteralPath $DenoExecutable)) {
    New-Item -ItemType Directory -Force -Path $DenoDirectory | Out-Null
    $DenoArchive = Join-Path ([System.IO.Path]::GetTempPath()) "tubedrop-deno-$DenoVersion.zip"
    try {
        Invoke-WebRequest `
            -Uri "https://github.com/denoland/deno/releases/download/v$DenoVersion/deno-x86_64-pc-windows-msvc.zip" `
            -OutFile $DenoArchive
        Expand-Archive -LiteralPath $DenoArchive -DestinationPath $DenoDirectory -Force
    }
    finally {
        Remove-Item -LiteralPath $DenoArchive -Force -ErrorAction SilentlyContinue
    }
}

$DenoSignature = Get-AuthenticodeSignature -LiteralPath $DenoExecutable
if ($DenoSignature.Status -ne "Valid") {
    throw "The downloaded Deno executable does not have a valid Authenticode signature."
}

python -m pip install --upgrade -r requirements-dev.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name TubeDrop `
    --add-data "assets;assets" `
    --add-binary "tools\deno\deno.exe;tools\deno" `
    --add-data "tools\deno\LICENSE-DENO.md;tools\deno" `
    --collect-all customtkinter `
    --collect-all yt_dlp `
    --collect-all yt_dlp_ejs `
    app.py

Write-Host "Built: $ProjectRoot\dist\TubeDrop.exe"
