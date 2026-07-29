$ErrorActionPreference = "Continue"
$srv = "C:\x3-project\server"

# 与 MakeLink.py 的 link_config 一一对应（key=链接路径, value=目标路径）
$links = [ordered]@{
    "ServerCommon/Common"                        = "../client/Assets/TFWCore/Script/Common"
    "ServerCommon/cspb/FrameworkProtos"          = "../client/Assets/TFWConfig/FrameworkProtos"
    "Libs/TfwProtobuf/Protobuf/protobuf-net"     = "../client/Packages/com.tfw.protobuf@1.0.1/Protobuf/protobuf-net"
    "GameServer/cspb/Protos"                     = "../client/Assets/Scripts/Protos"
    "GameServer/CSSharedCommon"                  = "../client/Assets/Scripts/CSShared/Common"
    "GameServer/CSSharedGame"                    = "../client/Assets/Scripts/CSShared/Game"
    "GameServer.Hotfix/CSSharedCommonHotfix"     = "../client/Assets/Scripts/CSSharedHotfix/Common"
    "GameServer.Hotfix/CSSharedGameHotfix"       = "../client/Assets/Scripts/CSSharedHotfix/Game"
    "MapServer/cspb/Protos"                      = "../client/Assets/Scripts/Protos"
    "MapServer/CSSharedCommon"                   = "../client/Assets/Scripts/CSShared/Common"
    "MapServer/CSSharedMap"                      = "../client/Assets/Scripts/CSShared/Map"
    "MapServer.Hotfix/CSSharedCommonHotfix"      = "../client/Assets/Scripts/CSSharedHotfix/Common"
    "MapServer.Hotfix/CSSharedMapHotfix"         = "../client/Assets/Scripts/CSSharedHotfix/Map"
    "CenterServer/cspb/Protos"                   = "../client/Assets/Scripts/Protos"
    "CenterServer/CSSharedCommon"                = "../client/Assets/Scripts/CSShared/Common"
    "CenterServer/CSSharedCenter"                = "../client/Assets/Scripts/CSShared/Center"
    "CenterServer.Hotfix/CSSharedCommonHotfix"   = "../client/Assets/Scripts/CSSharedHotfix/Common"
    "CenterServer.Hotfix/CSSharedCenterHotfix"   = "../client/Assets/Scripts/CSSharedHotfix/Center"
    "Resource/Assets/Res/MapCommon"              = "../client/Assets/Res/MapCommon"
    "Resource/Assets/Res/Config/ProtoGen"        = "../client/Assets/Res/Config/ProtoGen"
}

$ok = 0; $skip = 0; $fail = 0
foreach ($k in $links.Keys) {
    $linkPath   = [System.IO.Path]::GetFullPath((Join-Path $srv $k))
    $targetPath = [System.IO.Path]::GetFullPath((Join-Path $srv $links[$k]))

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Host "MISSING-TARGET  $k  ->  $targetPath"; $fail++; continue
    }
    if (Test-Path -LiteralPath $linkPath) {
        Write-Host "EXISTS-SKIP     $k"; $skip++; continue
    }
    $parent = Split-Path -Parent $linkPath
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }

    try {
        New-Item -ItemType Junction -Path $linkPath -Target $targetPath -ErrorAction Stop | Out-Null
        Write-Host "OK              $k"; $ok++
    } catch {
        Write-Host "FAIL            $k  :  $($_.Exception.Message)"; $fail++
    }
}
Write-Host ""
Write-Host "==== 建成 $ok / 跳过 $skip / 失败 $fail ===="
