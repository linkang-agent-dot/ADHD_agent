# 打开Chrome并导航到携程机票
$url = "https://flights.ctrip.com/domestic/round-trip?depCity=Shanghai&arrCity=&depDate=2026-04-30&retDate=2026-05-04&cabinType=Y&nonstop=1&roundTrip=1"
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"

if (Test-Path $chromePath) {
    Start-Process $chromePath -ArgumentList "--remote-debugging-port=9222", $url
} else {
    Start-Process "chrome.exe" -ArgumentList "--remote-debugging-port=9222", $url
}
