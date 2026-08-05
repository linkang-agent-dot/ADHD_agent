$ErrorActionPreference = "Stop"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$here = $PSScriptRoot
$out = "C:\ADHD_agent\KB\产出-数值设计\X3_挖孔搬运\05_界面重做静态图"
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }
Get-ChildItem -Path $here -Filter *.html | ForEach-Object {
  $name = $_.BaseName
  $png = Join-Path $out ($name + ".png")
  $url = "file:///" + ($_.FullName -replace '\\', '/')
  & $chrome --headless=new --disable-gpu --hide-scrollbars --no-sandbox `
    --force-device-scale-factor=1 --window-size=1080,1920 `
    --default-background-color=00000000 `
    --screenshot="$png" "$url" 2>$null | Out-Null
  if (Test-Path $png) { "OK  $name" } else { "FAIL $name" }
}
