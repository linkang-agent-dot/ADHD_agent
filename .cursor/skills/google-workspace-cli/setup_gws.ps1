# Google Workspace CLI 一键部署脚本
# 使用方法: 以管理员身份运行 PowerShell，执行此脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Workspace CLI 一键部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤 1: 检查并安装 Node.js
Write-Host "[1/5] 检查 Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "  ✓ Node.js 已安装: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js 未安装，请先安装 Node.js: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# 步骤 2: 安装 gws CLI
Write-Host ""
Write-Host "[2/5] 安装 gws CLI..." -ForegroundColor Yellow
$gwsVersion = gws --version 2>$null
if ($gwsVersion) {
    Write-Host "  ✓ gws CLI 已安装: $gwsVersion" -ForegroundColor Green
} else {
    Write-Host "  → 正在安装 gws CLI..." -ForegroundColor Cyan
    npm install -g @googleworkspace/cli
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ gws CLI 安装成功" -ForegroundColor Green
    } else {
        Write-Host "  ✗ gws CLI 安装失败" -ForegroundColor Red
        exit 1
    }
}

# 步骤 3: 创建配置目录
Write-Host ""
Write-Host "[3/5] 创建配置目录..." -ForegroundColor Yellow
$configDir = "$env:USERPROFILE\.config\gws"
if (Test-Path $configDir) {
    Write-Host "  ✓ 配置目录已存在: $configDir" -ForegroundColor Green
} else {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "  ✓ 配置目录已创建: $configDir" -ForegroundColor Green
}

# 步骤 4: 检查凭据文件
Write-Host ""
Write-Host "[4/5] 检查 OAuth 凭据..." -ForegroundColor Yellow
$clientSecret = "$configDir\client_secret.json"
if (Test-Path $clientSecret) {
    Write-Host "  ✓ 凭据文件已存在: $clientSecret" -ForegroundColor Green
} else {
    Write-Host "  ! 凭据文件不存在" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  请按以下步骤配置 OAuth 凭据:" -ForegroundColor Cyan
    Write-Host "  1. 打开 https://console.cloud.google.com/projectcreate 创建项目" -ForegroundColor White
    Write-Host "  2. 配置 OAuth 同意屏幕 (External)" -ForegroundColor White
    Write-Host "  3. 添加测试用户 (你的邮箱)" -ForegroundColor White
    Write-Host "  4. 创建 OAuth 凭据 (Desktop app)" -ForegroundColor White
    Write-Host "  5. 下载 JSON 文件" -ForegroundColor White
    Write-Host ""
    
    $downloadPath = Read-Host "请输入下载的 JSON 文件完整路径"
    if (Test-Path $downloadPath) {
        Copy-Item $downloadPath $clientSecret
        Write-Host "  ✓ 凭据文件已复制" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 文件不存在: $downloadPath" -ForegroundColor Red
        exit 1
    }
}

# 步骤 5: 设置环境变量
Write-Host ""
Write-Host "[5/5] 配置环境变量..." -ForegroundColor Yellow

$projectId = $env:GOOGLE_WORKSPACE_PROJECT_ID
if ($projectId) {
    Write-Host "  ✓ 项目 ID 已设置: $projectId" -ForegroundColor Green
} else {
    $projectId = Read-Host "请输入 Google Cloud 项目 ID (如 calm-repeater-489707-n1)"
    [Environment]::SetEnvironmentVariable("GOOGLE_WORKSPACE_PROJECT_ID", $projectId, "User")
    $env:GOOGLE_WORKSPACE_PROJECT_ID = $projectId
    Write-Host "  ✓ 项目 ID 已保存" -ForegroundColor Green
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 启用 API (用创建项目的账号打开以下链接):" -ForegroundColor White
Write-Host "   - Drive: https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=$projectId" -ForegroundColor Cyan
Write-Host "   - Sheets: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=$projectId" -ForegroundColor Cyan
Write-Host "   - Docs: https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=$projectId" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. 授权登录:" -ForegroundColor White
Write-Host "   gws auth login" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. 测试:" -ForegroundColor White
Write-Host "   gws drive files list" -ForegroundColor Cyan
Write-Host ""
