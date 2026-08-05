$ErrorActionPreference = "Continue"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$here = $PSScriptRoot
$out = Join-Path $here "png"
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }
Get-ChildItem -Path $here -Filter *.html | ForEach-Object {
  $name = $_.BaseName
  $png = Join-Path $out ($name + ".png")
  $url = "file:///" + ($_.FullName.Replace([char]92, [char]47))
  & $chrome --headless=new --disable-gpu --hide-scrollbars --no-sandbox `
    --force-device-scale-factor=1 --window-size=1080,1920 `
    --default-background-color=00000000 `
    --screenshot="$png" "$url" 2>&1 | Out-Null
  if (Test-Path $png) { "OK  $name" } else { "FAIL $name" }
}
