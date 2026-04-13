@echo off
rem OpenClaw Gateway (v2026.3.13)
set "MINIMAX_API_KEY=sk-cp-UZlYE7WEtHwVEgCKEZOpgSNezyVxA3mTGdUy8k0nkNJindUuOv_bUj2GlxO1VI6eTizdHvoR8tEHzaDBhTf4WEBuF2OZTuQ-kYHxi-amwfRtV8VG2CRKlaE"
set "FEISHU_APP_SECRET=rrIWGubFOkGdmLSeNRSqbeSwYCJ1LP8m"
set "TMPDIR=C:\Users\linkang\AppData\Local\Temp"
set "OPENCLAW_GATEWAY_PORT=18790"
set "OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service"
set "OPENCLAW_WINDOWS_TASK_NAME=OpenClaw Gateway"
set "OPENCLAW_SERVICE_MARKER=openclaw"
set "OPENCLAW_SERVICE_KIND=gateway"
set "OPENCLAW_SERVICE_VERSION=2026.3.13"
"C:\Program Files\nodejs\node.exe" C:\Users\linkang\AppData\Roaming\npm\node_modules\openclaw\dist\index.js gateway --port 18790
